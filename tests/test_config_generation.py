import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config
from config.models.consolidated import AppConfig


class TestConfigGeneration:
    """Test configuration generation without errors."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear the config cache before each test."""
        get_config.cache_clear()
        yield
        get_config.cache_clear()

    def test_get_config_returns_appconfig_instance(self, clean_env, sample_env_file):
        """Test that get_config returns a valid AppConfig instance."""
        # Use sample .env file to avoid interference
        with patch("config.helpers.base.PATH_ENV", sample_env_file):
            config = get_config()
            assert isinstance(config, AppConfig)

    def test_config_has_required_sections(self, clean_env, sample_env_file):
        """Test that config has all required top-level sections."""
        with patch("config.helpers.base.PATH_ENV", sample_env_file):
            config = get_config()

            # Check that all major sections exist
            assert hasattr(config, "SERVICE_NAME")
            assert hasattr(config, "DB")
            assert hasattr(config, "AWS_CONFIG")
            assert hasattr(config, "LLM")
            assert hasattr(config, "LOOKUP_DATA")

    def test_config_default_values(self, clean_env):
        """Test that config loads with expected default values."""
        # Create a config without any env files to test pure defaults
        config = AppConfig(_env_file=None)

        assert config.SERVICE_NAME == "my_service_name"
        assert config.DB.PORT == 5432
        assert config.AWS_CONFIG.AWS_PROFILE == "default"
        assert config.LLM.VERBOSITY is False

    def test_config_caching(self, clean_env, sample_env_file):
        """Test that get_config returns the same instance (caching works)."""
        with patch("config.helpers.base.PATH_ENV", sample_env_file):
            config1 = get_config()
            config2 = get_config()

            # Should be the same object due to caching
            assert config1 is config2

    def test_config_model_validation(self, clean_env, sample_env_file):
        """Test that config passes Pydantic validation."""
        with patch("config.helpers.base.PATH_ENV", sample_env_file):
            config = get_config()

            # This should not raise any validation errors
            validated_data = config.model_validate(config.model_dump())
            assert validated_data is not None
