"""Unit tests for config module."""

import pytest
from unittest.mock import patch, MagicMock
from config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_initialization(self):
        """Test that Config initializes properly."""
        assert hasattr(Config, 'PORT')
        assert hasattr(Config, 'DAILY_POST_TIME')
        assert hasattr(Config, 'GITHUB_TOKEN')
        assert hasattr(Config, 'GROQ_API_KEY')

    def test_validate_config_success(self):
        """Test validate_config with valid config."""
        with patch.dict('os.environ', {
            'GITHUB_TOKEN': 'test_token',
            'GROQ_API_KEY': 'test_key',
            'LINKEDIN_ACCESS_TOKEN': 'test_linkedin'
        }):
            # Should not raise exception
            Config.validate_config()

    def test_validate_config_missing_github(self):
        """Test validate_config with missing GitHub token."""
        with patch.object(Config, 'GITHUB_TOKEN', None):
            with patch.object(Config, 'GROQ_API_KEY', 'test'):
                with patch.object(Config, 'LINKEDIN_ACCESS_TOKEN', 'test'):
                    with pytest.raises(ValueError, match="GITHUB_TOKEN is required"):
                        Config.validate_config()

    def test_validate_config_missing_groq(self):
        """Test validate_config with missing Groq key."""
        with patch.object(Config, 'GITHUB_TOKEN', 'test'):
            with patch.object(Config, 'GROQ_API_KEY', None):
                with patch.object(Config, 'LINKEDIN_ACCESS_TOKEN', 'test'):
                    with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
                        Config.validate_config()

    def test_port_default(self):
        """Test PORT default value."""
        # PORT is set at class definition time, should be 5000 by default
        assert Config.PORT == 5000

    def test_daily_post_time_default(self):
        """Test DAILY_POST_TIME default value."""
        assert Config.DAILY_POST_TIME == "18:00"
