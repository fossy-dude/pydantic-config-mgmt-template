import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def clean_env():
    """Clean environment variables before and after test."""
    # Store original env vars
    original_env = dict(os.environ)

    # Clean test-related env vars
    test_vars = [
        "SERVICE_NAME",
        "DB__HOST",
        "DB__USERNAME",
        "DB__PASSWORD",
        "AWS_CONFIG__S3_BUCKET_NAMES__BUCKET_A",
        "LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY",
    ]

    for var in test_vars:
        os.environ.pop(var, None)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def temp_secrets_dir(temp_project_dir):
    """Create a temporary secrets directory."""
    secrets_dir = temp_project_dir / "secrets"
    secrets_dir.mkdir()
    return secrets_dir


@pytest.fixture
def temp_dotenv_file(temp_project_dir):
    """Create a temporary .env file."""
    env_file = temp_project_dir / ".env"
    return env_file


@pytest.fixture
def sample_env_file(temp_project_dir):
    """Create a temporary sample .env file for testing."""
    env_file = temp_project_dir / ".env.sample"

    # Create sample content
    sample_content = """# Sample environment variables
# Copy this file to .env and modify the values as needed

SERVICE_NAME="sample_service_name"
DB__HOST="sample.host.com"
DB__USERNAME="sample_username"
DB__PASSWORD="sample_password"
AWS_CONFIG__S3_BUCKET_NAMES__BUCKET_A="sample-bucket"
LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY="sk-sample-api-key"
"""

    env_file.write_text(sample_content)
    yield env_file

    # Cleanup after test
    if env_file.exists():
        env_file.unlink()
