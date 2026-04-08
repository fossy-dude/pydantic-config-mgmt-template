# External Packages
import functools
import os

from config.models.consolidated import AppConfig
from utils.logging_helpers import get_logger

logger = get_logger(__name__)


def map_env_aliases_to_supported_env_vars() -> None:
    """
    Map common environment variable aliases to Pydantic nested env var names.

    Pydantic Settings uses the ``__`` delimiter to resolve nested model fields
    from environment variables (e.g. ``AWS__AWS_PROFILE`` maps to
    ``AppConfig.AWS.AWS_PROFILE``). This function copies well-known flat AWS
    environment variable names into the corresponding nested names so that
    both conventions are accepted transparently.

    Notes
    -----
    Only copies a variable when the source key is present in the environment;
    existing values for the target key are not preserved.
    """

    def map(target, source):
        if os.environ.get(source):
            os.environ[target] = os.environ[source]

    map("AWS__AWS_PROFILE", "AWS_PROFILE")
    map("AWS__AWS_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID")
    map("AWS__AWS_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY")
    map("AWS__AWS_DEFAULT_REGION", "AWS_DEFAULT_REGION")


@functools.cache
def get_config() -> AppConfig:
    """Get the app configuration (using secrets, dotenv, config file and environment file)."""
    # Map some common aliases to env variables to supported env variables
    map_env_aliases_to_supported_env_vars()

    # Load config from aws secrets, secret files, env, dotenv, yaml and other sources
    config = AppConfig()

    return config


if __name__ == "__main__":
    logger.info(get_config())
