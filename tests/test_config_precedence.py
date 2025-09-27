import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.models.consolidated import AppConfig


class TestConfigPrecedence:
    """Test configuration source precedence: secrets > env vars > dotenv > defaults."""

    def test_secrets_override_env_vars(self, clean_env, temp_secrets_dir):
        """Test that secrets have higher precedence than environment variables."""
        # Set environment variable
        os.environ["SERVICE_NAME"] = "env_service"

        # Create secret file
        secret_file = temp_secrets_dir / "SERVICE_NAME"
        secret_file.write_text("secret_service")

        # Create config with custom secrets directory
        config = AppConfig(_secrets_dir=str(temp_secrets_dir))

        # Secret should take precedence
        assert config.SERVICE_NAME == "secret_service"

    def test_env_vars_override_dotenv(self, clean_env, temp_dotenv_file):
        """Test that environment variables have higher precedence than dotenv files."""
        # Create .env file
        temp_dotenv_file.write_text("SERVICE_NAME=dotenv_service\n")

        # Set environment variable
        os.environ["SERVICE_NAME"] = "env_service"

        # Create config with custom env file
        config = AppConfig(_env_file=str(temp_dotenv_file))

        # Environment variable should take precedence
        assert config.SERVICE_NAME == "env_service"

    def test_dotenv_override_defaults(self, clean_env, temp_dotenv_file):
        """Test that dotenv files have higher precedence than defaults."""
        # Create .env file
        temp_dotenv_file.write_text("SERVICE_NAME=dotenv_service\n")

        # Create config with custom env file
        config = AppConfig(_env_file=str(temp_dotenv_file))

        # Dotenv should override default
        assert config.SERVICE_NAME == "dotenv_service"

    def test_precedence_order_is_documented(self, clean_env):
        """Test that the precedence order is implemented as documented."""
        # This test verifies the precedence chain by testing each level
        # Secrets > Environment > Dotenv > Defaults

        # Test that environment vars override defaults
        os.environ["SERVICE_NAME"] = "env_test"
        config = AppConfig(_env_file=None)  # No env file
        assert config.SERVICE_NAME == "env_test"

        # The other precedence tests in this class verify:
        # - secrets_override_env_vars: secrets > environment
        # - env_vars_override_dotenv: environment > dotenv
        # - dotenv_override_defaults: dotenv > defaults
        # - full_precedence_chain: secrets > env > dotenv > defaults

    def test_dotenv_works_for_nested_config(self, clean_env, temp_dotenv_file):
        """Test that dotenv works for nested configuration values."""
        temp_dotenv_file.write_text("DB__PORT=9999\n")

        # Create config with only env file
        config = AppConfig(_env_file=str(temp_dotenv_file))

        # Dotenv value should be used
        assert config.DB.PORT == 9999

    def test_full_precedence_chain(self, clean_env, temp_secrets_dir, temp_dotenv_file):
        """Test the complete precedence chain: secrets > env > dotenv > default."""
        # Set up all sources
        secret_file = temp_secrets_dir / "SERVICE_NAME"
        secret_file.write_text("secret_value")

        os.environ["SERVICE_NAME"] = "env_value"
        temp_dotenv_file.write_text("SERVICE_NAME=dotenv_value\n")

        # Create config with both secrets dir and env file
        config = AppConfig(_secrets_dir=str(temp_secrets_dir), _env_file=str(temp_dotenv_file))

        # Secret should have highest precedence
        assert config.SERVICE_NAME == "secret_value"

    def test_missing_secret_falls_back_to_env(self, clean_env, temp_secrets_dir):
        """Test that missing secrets fall back to environment variables."""
        os.environ["SERVICE_NAME"] = "env_fallback"

        # No secret file created

        # Create config with custom secrets dir
        config = AppConfig(_secrets_dir=str(temp_secrets_dir))

        # Should fall back to environment variable
        assert config.SERVICE_NAME == "env_fallback"
