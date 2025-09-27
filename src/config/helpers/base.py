import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from config.helpers.get_project_basedir import get_project_basedir

# Build paths inside the project like this: BASE_DIR / 'subdir'.
PROJECT_BASE_DIR = get_project_basedir()
PATH_ENV = Path(PROJECT_BASE_DIR, ".env")


@dataclass
class ConfigSource:
    """Information about a configuration source."""

    source_type: str
    path: str
    available: bool
    description: str


# Global variable to track config sources during loading
_config_sources: list[ConfigSource] = []


def get_config_sources() -> list[ConfigSource]:
    """
    Get the list of configuration sources that were checked during config loading.

    Returns
    -------
    list[ConfigSource]
        list of configuration sources with availability information.
    """
    return _config_sources.copy()


def track_config_source(source_type: str, path: str, available: bool, description: str) -> None:
    """
    Track a configuration source during the loading process.

    Parameters
    ----------
    source_type : str
        Type of configuration source (e.g., 'yaml', 'env', 'dotenv', 'secrets').
    path : str
        Path or identifier for the source.
    available : bool
        Whether the source is available/readable.
    description : str
        Human-readable description of the source.
    """
    _config_sources.append(
        ConfigSource(
            source_type=source_type,
            path=path,
            available=available,
            description=description,
        )
    )


def clear_config_sources() -> None:
    """Clear the tracked configuration sources list."""
    global _config_sources
    _config_sources = []


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
    "extra": "forbid",
    "env_file": (PATH_ENV,),
    "secrets_dir": "/run/secrets",
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
    Base model for project's Pydantic models with configuration source priority handling.

    Notes
    -----
    Provides base settings configurations using DEFAULT_CONFIG_SETTINGS including:
    - case_sensitive: True (required for proper nested model env var sourcing)
    - env_nested_delimiter: "__" (for nested environment variables like DB__HOST)
    - env_file: Path to .env file in project root
    - secrets_dir: "/run/secrets" for Docker secrets support

    Configuration source priority (highest to lowest):
    1. Secrets (from /run/secrets directory)
    2. Environment variables
    3. Dotenv files (.env)
    4. YAML/JSON configuration files
    5. Default values in model definitions
    """

    model_config = SettingsConfigDict(**DEFAULT_CONFIG_SETTINGS)  # type: ignore[typeddict-item]

    def __init__(self, **data: Any) -> None:
        """Initialize the config model and track configuration sources."""
        # Track sources before calling parent init
        self._track_all_sources()
        super().__init__(**data)

    def _track_all_sources(self) -> None:
        """Track all possible configuration sources and their availability."""
        # Track secrets directory
        secrets_dir_value = self.model_config.get("secrets_dir", "/run/secrets")
        secrets_dir = Path(str(secrets_dir_value) if secrets_dir_value is not None else "/run/secrets")
        track_config_source(
            source_type="secrets",
            path=str(secrets_dir),
            available=secrets_dir.exists() and secrets_dir.is_dir(),
            description=f"Docker secrets directory: {secrets_dir}",
        )

        # Track environment variables (we can't easily check all possible env vars,
        # so we'll track that env vars are available as a source)
        track_config_source(
            source_type="environment",
            path="system environment",
            available=True,
            description="System environment variables",
        )

        # Track .env files
        env_files = self.model_config.get("env_file", ())
        if env_files is None:
            env_files = ()
        elif isinstance(env_files, (str, Path)):
            env_files = (env_files,)

        for env_file in env_files:
            env_path = Path(env_file)
            track_config_source(
                source_type="dotenv",
                path=str(env_path),
                available=env_path.exists() and env_path.is_file(),
                description=f"Dotenv file: {env_path}",
            )

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
        Customize the priority order of configuration sources.

        Parameters
        ----------
        settings_cls : Type[BaseSettings]
            The settings class being configured.
        init_settings : PydanticBaseSettingsSource
            Settings passed during model initialization.
        env_settings : PydanticBaseSettingsSource
            Settings from environment variables.
        dotenv_settings : PydanticBaseSettingsSource
            Settings from .env files.
        file_secret_settings : PydanticBaseSettingsSource
            Settings from secrets files (e.g., Docker secrets).

        Returns
        -------
        tuple[PydanticBaseSettingsSource, ...]
            tuple of settings sources in priority order (highest to lowest).

        Notes
        -----
        Priority order: secrets > environment variables > dotenv files > init settings.
        This ensures that secrets have the highest priority, followed by environment
        variables, then .env files, and finally default values from model initialization.

        Reference: https://docs.pydantic.dev/latest/concepts/pydantic_settings/#changing-priority
        """
        return file_secret_settings, env_settings, dotenv_settings, init_settings


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


def print_config_sources(logger: logging.Logger | None) -> None:
    """Print information about all configuration sources that were checked."""
    if logger is None:
        logger = logging.getLogger(__name__)
    sources = get_config_sources()
    if not sources:
        logger.info("No configuration sources tracked.")
        return
    msg = "Configuration sources checked during loading:\n"
    msg += "=" * 60

    for source in sources:
        status = "✓ Available" if source.available else "✗ Not available"
        msg += f"\n[{source.source_type.upper()}]: {status:>13} | {source.description}"

    msg += "\n" + "=" * 60
    msg += "\nPriority order: Secrets > Environment Variables > Dotenv Files > YAML > Defaults"
    logger.info(msg)
