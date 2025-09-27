import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config
from config.helpers.config_exporter import dump_config_to_yaml


class TestSensitiveDataHandling:
    """Test that model dump doesn't leak sensitive information."""

    @pytest.fixture(autouse=True)
    def setup_test_env(self, clean_env, sample_env_file):
        """Create a clean test environment and clear cache."""
        # Clear cache before each test
        get_config.cache_clear()

        # Mock to use sample .env file to avoid interference from real .env
        with patch("config.helpers.base.PATH_ENV", sample_env_file):
            yield

        # Clear cache after test
        get_config.cache_clear()

    def test_secret_str_fields_are_masked_in_model_dump(self, clean_env):
        """Test that SecretStr fields are properly masked in model dumps."""
        # Set some sensitive values
        os.environ["DB__USERNAME"] = "secret_username"
        os.environ["DB__PASSWORD"] = "secret_password"
        os.environ["LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY"] = "sk-secret-api-key"

        config = get_config()
        config_dict = config.model_dump()

        # Check that sensitive fields are masked
        assert str(config_dict["DB"]["USERNAME"]) == "**********"
        assert str(config_dict["DB"]["PASSWORD"]) == "**********"
        assert str(config_dict["LLM"]["OPENAI_MODEL_CONFIG"]["OPENAI_API_KEY"]) == "**********"

    def test_secret_str_fields_are_masked_in_json_dump(self, clean_env):
        """Test that SecretStr fields are masked in JSON mode dumps."""
        os.environ["DB__USERNAME"] = "secret_username"
        os.environ["LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY"] = "sk-secret-api-key"

        config = get_config()
        config_dict = config.model_dump(mode="json")

        # Check that sensitive fields are masked in JSON mode too
        assert config_dict["DB"]["USERNAME"] == "**********"
        assert config_dict["LLM"]["OPENAI_MODEL_CONFIG"]["OPENAI_API_KEY"] == "**********"

    def test_actual_secret_values_are_accessible(self, clean_env):
        """Test that actual secret values are accessible through get_secret_value()."""
        os.environ["DB__USERNAME"] = "actual_username"
        os.environ["DB__PASSWORD"] = "actual_password"

        config = get_config()

        # Actual values should be accessible via get_secret_value()
        assert config.DB.USERNAME.get_secret_value() == "actual_username"
        assert config.DB.PASSWORD.get_secret_value() == "actual_password"

        # But string representation should be masked
        assert str(config.DB.USERNAME) == "**********"
        assert str(config.DB.PASSWORD) == "**********"

    def test_dump_config_to_yaml_masks_secrets(self, clean_env, temp_project_dir):
        """Test that dump_config_to_yaml properly masks sensitive information."""
        os.environ["DB__USERNAME"] = "secret_db_user"
        os.environ["LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY"] = "sk-secret-key"

        # Mock PROJECT_BASE_DIR for testing
        from unittest.mock import patch  # noqa: PLC0415

        with patch("config.helpers.config_exporter.PROJECT_BASE_DIR", temp_project_dir):
            dump_config_to_yaml("test_config.yaml")

            # Read the generated file
            config_file = temp_project_dir / "test_config.yaml"
            content = config_file.read_text()

            # Verify sensitive data is masked
            assert "secret_db_user" not in content
            assert "sk-secret-key" not in content
            assert "**********" in content

    def test_no_sensitive_data_in_yaml_output(self, clean_env, temp_project_dir):
        """Test that YAML output contains no actual sensitive values."""
        # Set various sensitive values
        sensitive_values = [
            "super_secret_password",
            "sk-1234567890abcdef",
            "mysql://user:pass@host:3306/db",
            "secret_api_token",
        ]

        os.environ["DB__PASSWORD"] = sensitive_values[0]
        os.environ["LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY"] = sensitive_values[1]

        from unittest.mock import patch  # noqa: PLC0415

        with patch("config.helpers.config_exporter.PROJECT_BASE_DIR", temp_project_dir):
            dump_config_to_yaml("security_test.yaml")

            config_file = temp_project_dir / "security_test.yaml"
            content = config_file.read_text()

            # Verify none of the sensitive values appear in the output
            for sensitive_value in sensitive_values:
                assert sensitive_value not in content, f"Sensitive value '{sensitive_value}' found in YAML output"

    def test_model_dump_json_preserves_masking(self, clean_env):
        """Test that JSON dumps also preserve secret masking."""
        os.environ["DB__USERNAME"] = "json_test_user"

        config = get_config()
        json_str = config.model_dump_json()

        # Check that the actual secret is not in the JSON string
        assert "json_test_user" not in json_str
        assert "**********" in json_str

    def test_nested_secret_fields_are_masked(self, clean_env):
        """Test that nested SecretStr fields are properly masked."""
        os.environ["LLM__OPENAI_MODEL_CONFIG__OPENAI_API_KEY"] = "nested_secret_key"

        config = get_config()
        config_dict = config.model_dump()

        # Check nested structure
        assert "LLM" in config_dict
        assert "OPENAI_MODEL_CONFIG" in config_dict["LLM"]
        assert "OPENAI_API_KEY" in config_dict["LLM"]["OPENAI_MODEL_CONFIG"]

        # Check that nested secret is masked
        assert str(config_dict["LLM"]["OPENAI_MODEL_CONFIG"]["OPENAI_API_KEY"]) == "**********"
