# External Packages
import functools
from pathlib import Path

from config.helpers.base import clear_config_sources, print_config_sources, track_config_source
from config.helpers.config_parser import parse_yaml_file_as_dict
from config.helpers.get_project_basedir import get_project_basedir
from config.helpers.logging_setup import get_logger, setup_logging
from config.models.consolidated import AppConfig

logger = get_logger(__name__)


# ----------------------- Default project configuration ---------------------- #
def load_config_yaml(filename: str = "config.yaml") -> dict | None:
    path_config = Path(get_project_basedir(), filename)

    # Track YAML config file source
    track_config_source(
        source_type="yaml",
        path=str(path_config),
        available=path_config.exists() and path_config.is_file(),
        description=f"YAML configuration file: {filename}",
    )

    if not path_config.exists():
        logger.warning(f"Config file not found at expected path : '{path_config}'. Not using it as config source.")
        return None

    try:
        config_dict = parse_yaml_file_as_dict(path_config)
        return config_dict
    except Exception:
        return None


@functools.lru_cache(maxsize=None)
def get_config() -> AppConfig:
    # Clear any previous source tracking
    clear_config_sources()

    # Load YAML config (this will track the YAML source)
    yaml_config = load_config_yaml()
    if yaml_config is None:
        yaml_config = {}

    # Create config instance (this will track other sources via BaseConfigModel)
    config = AppConfig(**yaml_config)

    # Setup logging
    setup_logging(config.LOGGING)
    logger = get_logger(__name__)
    # Print configuration sources information
    print_config_sources(logger=logger)

    return config


if __name__ == "__main__":
    logger.info(get_config())
