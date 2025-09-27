from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from config import get_config, get_logger
from config.helpers.get_project_basedir import get_project_basedir

logger = get_logger(__name__)


def dump_config_to_yaml(filename: str = "config_dump.yaml") -> None:
    """
    Dump the current configuration to a YAML file.

    Parameters
    ----------
    filename : str, optional
        The filename to write the configuration to, by default "config.yaml"
        The file will be created in the project base directory.
    """
    config = get_config()
    config_dict = config.model_dump(mode="json")  # Use JSON mode for better serialization

    output_path = Path(get_project_basedir(), filename)

    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)

    with output_path.open("w") as f:
        yaml.dump(config_dict, f)

    logger.info(f"Configuration dumped to: {output_path}")


def _flatten_config_dict(
    config_dict: dict[str, Any],
    parent_key: str = "",
    sep: str = "__",
    null_value="None",
    skip_secret_values: bool = True,
) -> dict[str, str]:
    """
    Flatten a nested dictionary into dotenv format with custom separator.

    Parameters
    ----------
    config_dict : dict[str, Any]
        The nested configuration dictionary to flatten.
    parent_key : str, optional
        The parent key prefix, by default ""
    sep : str, optional
        The separator to use between nested keys, by default "__"
    null_value : str, optional
        The value used to represent a null value, by default "None"
    skip_secret_values: bool, optional
        Whether to skip secret values, by default True

    Returns
    -------
    dict[str, str]
        Flattened dictionary with string keys and string values.
    """
    items = []

    for key, value in config_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(_flatten_config_dict(value, new_key, sep=sep).items())
        elif isinstance(value, list):
            # Convert lists to comma-separated strings
            items.append((new_key, ",".join(str(item) for item in value)))
        elif value is None:
            items.append((new_key, null_value))
        elif isinstance(value, bool):
            # Convert boolean to lowercase string for dotenv compatibility
            items.append((new_key, str(value).lower()))
        elif isinstance(value, str):
            if value.startswith("********") and skip_secret_values is True:
                continue
            else:
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
    flat_config = _flatten_config_dict(config_dict)

    output_path = Path(get_project_basedir(), filename)

    with output_path.open("w") as f:
        for key, value in sorted(flat_config.items()):
            # Enclose values containing spaces in single quotes
            if " " in str(value):
                f.write(f"{key}='{value}'\n")
            else:
                f.write(f"{key}={value}\n")

    logger.info(f"Configuration dumped to dotenv format: {output_path}")


if __name__ == "__main__":
    dump_config_to_dotenv()
    dump_config_to_yaml()
