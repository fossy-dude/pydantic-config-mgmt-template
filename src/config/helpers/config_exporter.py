import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any

from config import get_config
from config.helpers.get_project_basedir import get_project_basedir
from pydantic import SecretStr
from pydantic_core import PydanticUndefinedType
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

logger = logging.getLogger(__name__)


def _build_commented_map(data: dict[str, Any], model_instance: Any, indent: int = 0) -> CommentedMap:
    """
    Recursively build a CommentedMap, injecting Pydantic field descriptions as YAML comments.

    For fields that have a static default value, the comment is extended to include it,
    e.g. ``# Description of the field (default: 54)``. SecretStr defaults are masked as ``***``.

    Parameters
    ----------
    data : dict[str, Any]
        The dictionary data (from model_dump) to convert.
    model_instance : Any
        The Pydantic model instance used to extract field descriptions.
    indent : int, optional
        Current indentation depth (in spaces) used to align comment ``#`` characters, by default 0.

    Returns
    -------
    CommentedMap
        A ruamel.yaml CommentedMap with comments derived from field descriptions.
    """
    commented: CommentedMap = CommentedMap()
    # model_fields is a class-level attribute in Pydantic v2
    model_fields = getattr(type(model_instance), "model_fields", {}) if model_instance is not None else {}

    for key, value in data.items():
        field_info = model_fields.get(key)

        if isinstance(value, dict):
            # Recurse into nested Pydantic models; child keys are indented by +2
            sub_instance = getattr(model_instance, key, None) if model_instance is not None else None
            if sub_instance is not None and hasattr(type(sub_instance), "model_fields"):
                commented[key] = _build_commented_map(value, sub_instance, indent=indent + 2)
            else:
                # Plain dict with no associated Pydantic model — copy as-is
                inner: CommentedMap = CommentedMap()
                for k, v in value.items():
                    inner[k] = v
                commented[key] = inner
        else:
            commented[key] = value

        # Attach the field description (and default value when available) as a comment above the key
        if field_info is not None and field_info.description:
            comment = field_info.description

            # Append the default value to the comment if one exists (skip PydanticUndefined / None defaults)
            default = field_info.default
            has_default = default is not None and not isinstance(default, PydanticUndefinedType)
            if has_default:
                # Mask SecretStr defaults so secrets are never written in plain text
                if isinstance(default, SecretStr):
                    default_repr: Any = "***"
                elif isinstance(default, Enum):
                    # Use the underlying value so comments show e.g. "us-east-1" instead of "Region.US_EAST_1"
                    default_repr = default.value
                elif isinstance(default, (str, int, float, bool)):
                    # Primitive types are safe to use directly
                    default_repr = default
                else:
                    # Fallback for any other complex type
                    default_repr = str(default)
                comment = f"{comment} (default: {default_repr})"

            commented.yaml_set_comment_before_after_key(key, before=comment, indent=indent)

    return commented


def dump_config_to_yaml(filename: str = "config_dump.yaml", **kwargs) -> None:
    """
    Dump the current configuration to a YAML file.

    Each config parameter that has a Pydantic ``Field(description=...)`` will have
    its description written as a ``# comment`` on the line immediately above it.

    Parameters
    ----------
    filename : str, optional
        The filename to write the configuration to, by default "config_dump.yaml".
        The file will be created in the project base directory.
    """
    config = get_config()
    config_dict = config.model_dump(mode="json", **kwargs)  # Use JSON mode for better serialization

    # Build a CommentedMap so ruamel.yaml preserves the description comments
    commented_config = _build_commented_map(config_dict, config)

    output_path = Path(get_project_basedir(), filename)

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)

    with output_path.open("w") as f:
        yaml.dump(commented_config, f)

    logger.info(f"Configuration dumped to: {output_path}")


def _flatten_config_dict(
    config_dict: dict[str, Any],
    config: Any,
    parent_key: str = "",
    sep: str = "__",
    null_value: str | None = None,
    include_plain_secret_values: bool = False,
) -> dict[str, str]:
    """
    Flatten a nested dictionary into dotenv format with custom separator.

    Parameters
    ----------
    config_dict : Dict[str, Any]
        The nested configuration dictionary to flatten.
    config : Any
        The original pydantic model to access SecretStr objects.
    parent_key : str, optional
        The parent key prefix, by default ""
    sep : str, optional
        The separator to use between nested keys, by default "__"
    null_value : str, optional
        The value used to represent a null value, by default set to None. In dotenv files, will show up as "KEY=None"
    include_plain_secret_values: bool, optional
        Whether to include plain secret values by calling get_secret_value(), by default False

    Returns
    -------
    Dict[str, str]
        Flattened dictionary with string keys and string values.
    """
    items = []

    for key, value in config_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        # Get the original value from the config model
        config_value = getattr(config, key, None)

        if isinstance(value, dict):
            items.extend(
                _flatten_config_dict(
                    value,
                    config_value,
                    new_key,
                    sep=sep,
                    null_value=null_value,
                    include_plain_secret_values=include_plain_secret_values,
                ).items()
            )
        elif isinstance(value, list):
            # Convert lists to comma-separated strings
            items.append((new_key, ",".join(str(item) for item in value)))
        elif value is None:
            items.append((new_key, null_value))
        elif isinstance(value, bool):
            # Convert boolean to lowercase string for dotenv compatibility
            items.append((new_key, str(value).lower()))
        elif isinstance(config_value, SecretStr):
            # Check if the original value in the config model is a SecretStr
            if include_plain_secret_values:
                items.append((new_key, config_value.get_secret_value()))
            else:
                items.append((new_key, str(value)))
        elif isinstance(value, str):
            items.append((new_key, value))
        else:
            items.append((new_key, str(value)))

    return dict(items)


def dump_config_to_dotenv(filename: str = ".env.dump", **kwargs) -> None:
    """
    Dump the current configuration to a dotenv file.

    Nested configuration elements are flattened using double underscores (__) as separators.
    For example, AWS.REGION becomes AWS__REGION in the dotenv file.

    Parameters
    ----------
    filename : str, optional
        The filename to write the configuration to, by default ".env.dump"
        The file will be created in the project base directory.
    kwargs: Any
        Additional keyword arguments to pass to pydantic's model_dump
    """
    config = get_config()
    config_dict = config.model_dump(mode="json", **kwargs)  # Use JSON mode for better serialization

    # Flatten the nested configuration
    flat_config = _flatten_config_dict(config_dict, config)

    output_path = Path(get_project_basedir(), filename)

    with output_path.open("w") as f:
        for key, value in sorted(flat_config.items()):
            # Enclose values containing spaces in single quotes
            if " " in str(value):
                f.write(f"{key}='{value}'\n")
            else:
                f.write(f"{key}={value}\n")

    logger.info(f"Configuration dumped to dotenv format: {output_path}")


def dump_config_to_json(
    filename: str = "config_dump.json",
    include_plain_secret_values: bool = False,
    in_aws_format: bool = False,
    **kwargs,
) -> None:
    """
    Dump the current configuration to a JSON file shaped like AWS Lambda env vars.

    The output is a single-level mapping of strings suitable for the Lambda
    Environment variable payload (no nested objects).

    Parameters
    ----------
    filename : str, optional
        The filename to write the configuration to, by default "lambda_env.json".
        The file will be created in the project base directory.
    include_plain_secret_values : bool, optional
        Whether to include plain secret values by calling get_secret_value(), by default False.
    in_aws_format : bool, optional
        Whether to format the output in AWS Lambda environment variable format, by default False.
    kwargs: Any
        Additional keyword arguments to pass to pydantic's model_dump.
    """
    config = get_config()
    config_dict = config.model_dump(mode="json", **kwargs)

    # Flatten to a string-only mapping that matches Lambda's env var expectations
    flat_config = _flatten_config_dict(
        config_dict,
        config,
        include_plain_secret_values=include_plain_secret_values,
    )

    output_path = Path(get_project_basedir(), filename)
    if in_aws_format:
        # Wrap in AWS Lambda env var format
        flat_config = {"Variables": flat_config}

    with output_path.open("w") as f:
        json.dump(flat_config, f, sort_keys=True)

    logger.info(f"Configuration dumped to Lambda env JSON: {output_path}")


if __name__ == "__main__":
    dump_config_to_dotenv(exclude_unset=True)
    dump_config_to_yaml(exclude_unset=True)
    dump_config_to_json(exclude_unset=True)
