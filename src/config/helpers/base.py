from pathlib import Path
from typing import Annotated, Any

from pydantic import BeforeValidator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from config.helpers.aws_secrets import get_aws_secrets_key, should_use_aws_secrets_as_config_source
from config.helpers.get_project_basedir import get_project_basedir
from utils.pydantic_aws_secrets_mgr import AWSSecretsManagerSettingsSource

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_BASE_DIR = get_project_basedir()
PATH_ENV = Path(PROJECT_BASE_DIR, ".env")


def convert_to_absolute_path(path: str | Path) -> Path:
    """Convert a Path object to its absolute form (incl expanding user home dir paths) and returns the resolved path."""
    x = Path(path).expanduser()
    if not x.is_absolute():
        x = Path(get_project_basedir(), path)
    return x.resolve()


PathLike = str | Path
AbsolutePath = Annotated[PathLike, BeforeValidator(convert_to_absolute_path)]

DEFAULT_CONFIG_SETTINGS = {
    # Due to a pydantic bug,case_sensitive has to be set to True. Nested models don't get sourced correctly if False
    "case_sensitive": True,
    "arbitrary_types_allowed": False,
    "env_nested_delimiter": "__",
    "extra": "ignore",
    "env_file": (PATH_ENV,),
    "secrets_dir": "/run/secrets",
    "validate_by_name": True,
    "validate_by_alias": True,
}


def get_default_config_settings() -> dict[str, Any]:
    """
    Get the default configuration settings dictionary.

    Returns
    -------
    dict[str, Any]
        Dictionary containing default Pydantic settings configuration including
        case sensitivity, environment variable handling, and file paths.

    Notes
    -----
    Returns a copy of DEFAULT_CONFIG_SETTINGS which includes settings for:
    - case_sensitive: True (required for nested model env var sourcing)
    - env_nested_delimiter: "__" (for nested environment variables)
    - env_file: Path to .env file in project root
    - secrets_dir: "/run/secrets" for Docker secrets support
    """
    return DEFAULT_CONFIG_SETTINGS


class BaseConfigModel(BaseSettings):
    """
    Base model for project's other pydantic models.
    - Provides base settings configurations (using base.DEFAULT_CONFIG_SETTINGS)
    - Provides default priority for sourcing settings (Env variables > Secrets > Dotenv vars > json/yaml/ other sources)
    """

    model_config = SettingsConfigDict(**DEFAULT_CONFIG_SETTINGS)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Prefer environment variables when available, followed by default configuration (from json/yaml).
        Source - https://docs.pydantic.dev/latest/concepts/pydantic_settings/#changing-priority
        """
        # Add yaml file as source

        yml_src = YamlConfigSettingsSource(
            settings_cls=settings_cls, yaml_file=Path(get_project_basedir(), "config.yaml")
        )
        if should_use_aws_secrets_as_config_source():
            kwargs = {
                _: DEFAULT_CONFIG_SETTINGS.get(_)
                for _ in [
                    "case_sensitive",
                    "env_nested_delimiter",
                    "env_parse_enums",
                    "env_parse_none_str",
                    "env_prefix",
                ]
            }
            aws_secrets_src = AWSSecretsManagerSettingsSource(
                settings_cls=settings_cls, secret_id=get_aws_secrets_key(), **kwargs
            )
            return env_settings, aws_secrets_src, file_secret_settings, dotenv_settings, yml_src, init_settings
        return env_settings, file_secret_settings, dotenv_settings, yml_src, init_settings


# Custom types with validators for common use-cases


def assert_file_exists(path: Path) -> Path:
    """
    Check if a file exists, and return Path object if True.

    Parameters
    ----------
    path : Path
        The file path to verify

    Returns
    -------
    Path
        A Path object representing the existing file.

    Raises
    ------
    AssertionError
        If the file does not exist at the specified path.

    Notes
    -----
    Process flow:
    * Converts input to Path object and expands user directory references (~)
    * If path is relative, resolves it against PROJECT_BASE_DIR
    * Verifies the file exists and is a regular file
    * Returns the Path object of the verified file
    """
    assert path.is_file() and path.exists(), "File not found at path"
    return path


def assert_dir_exists(path: Path) -> Path:
    """
    Assert that a directory exists, creating it if necessary.

    Parameters
    ----------
    path : Path
        The path to the directory.  Can be relative to the project directory.

    Returns
    -------
    Path
        The absolute Path object representing the directory.

    Raises
    ------
    AssertionError
        If the provided path does not resolve to an existing directory after attempting creation.

    Notes
    -----
    This function attempts to create the directory using `mkdir(exist_ok=True, parents=True)`.
    If this fails for any reason, it proceeds without raising an exception. It then asserts that the directory exists.

    Process Flow:
    * Expands the user's home directory from the input `value` if it contains '~'.
    * If the path is relative, it resolves it to a path relative to `PROJECT_BASE_DIR`.
    * Attempts to create the directory with `mkdir(exist_ok=True, parents=True)`.  Ignores any exceptions during creation.
    * Asserts that the directory exists and is a directory. If not, raises an AssertionError.
    * Returns the absolute Path object.

    """
    try:
        path.mkdir(exist_ok=True, parents=True)
    except Exception:
        pass
    assert path.is_dir() and path.exists(), "Not a valid folder"
    return path


# PathType - Simple wrapper around pathlib.Path - validates if a path exists and is valid
RequiredFile = Annotated[
    PathLike,
    BeforeValidator(assert_file_exists),
    BeforeValidator(convert_to_absolute_path),
]
RequiredFolder = Annotated[
    PathLike,
    BeforeValidator(assert_dir_exists),
    BeforeValidator(convert_to_absolute_path),
]
