import os

from dotenv import load_dotenv

from config.helpers.get_project_basedir import get_project_basedir


def get_aws_secrets_key() -> str:
    """
    Get the AWS secrets manager key for the current environment.

    Returns
    -------
    str
        The name of the AWS secret to fetch configuration from.
    """
    # FIXME: Update with actual aws secrets pattern
    return "<secrets_name>"


def should_use_aws_secrets_as_config_source() -> bool:
    """
    Check if AWS Secrets Manager should be used as a configuration source.

    Returns
    -------
    bool
        True if AWS Secrets Manager should be used, False otherwise.
    """
    load_dotenv(get_project_basedir() / ".env")
    env = os.environ.get("ENABLE_AWS_SECRETS_CONFIG")
    if env is None:
        enable = False
    elif isinstance(env, (int, bool)):
        enable = bool(env)
    elif isinstance(env, str):
        enable = False if (env.lower() in ("false", "0", "no", "n")) else True
    return enable
