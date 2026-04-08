import os

from config.helpers.get_project_basedir import get_project_basedir


def get_aws_secrets_key():
    env = os.environ.get("env", "dev")
    # FIXME: Update with actual aws secrets pattern
    return f"<secrets_name>"


def should_use_aws_secrets_as_config_source() -> bool:
    from dotenv import load_dotenv

    load_dotenv(get_project_basedir() / ".env")
    env = os.environ.get("ENABLE_AWS_SECRETS_CONFIG")
    if env is None:
        enable = False
    elif isinstance(env, (int, bool)):
        enable = bool(env)
    elif isinstance(env, str):
        enable = False if (env.lower() in ("false", "0", "no", "n")) else True
    return enable
