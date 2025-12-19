"""
Configuration module for GitHub-to-Social AI Automation.

This module handles environment variable loading and configuration settings.
"""

import os
import logging
from dotenv import load_dotenv

# Configure logging for config module
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded from .env file")

class Config:
    """Configuration class to hold all application settings."""

    # GitHub Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
    GITHUB_REPO_OWNER = os.getenv('GITHUB_REPO_OWNER')
    GITHUB_REPO_NAME = os.getenv('GITHUB_REPO_NAME')

    # LinkedIn Configuration
    LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')

    # AI Configuration (Groq)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    # Server Configuration
    PORT = int(os.getenv('PORT', 5000))

    # Scheduling Configuration
    DAILY_POST_TIME = os.getenv('DAILY_POST_TIME', '18:00')  # UTC time

    # Review Configuration
    REQUIRE_POST_REVIEW = os.getenv('REQUIRE_POST_REVIEW', 'true').lower() == 'true'

    # Pipedream Configuration (optional)
    PIPEDREAM_WEBHOOK_URL = os.getenv('PIPEDREAM_WEBHOOK_URL')
    USE_PIPEDREAM = bool(PIPEDREAM_WEBHOOK_URL)

    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        required_vars = [
            'GITHUB_TOKEN',
            'GITHUB_WEBHOOK_SECRET',
            'GROQ_API_KEY'
        ]

        # LinkedIn token is optional if using Pipedream
        if not cls.USE_PIPEDREAM:
            required_vars.append('LINKEDIN_ACCESS_TOKEN')

        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Log configuration status
        logger.info("Configuration validation successful")
        logger.info(f"Server will run on port {cls.PORT}")
        logger.info(f"Daily posts scheduled for {cls.DAILY_POST_TIME} UTC")
        logger.info(f"Post review required: {cls.REQUIRE_POST_REVIEW}")
        logger.info(f"Using Pipedream for posting: {cls.USE_PIPEDREAM}")

        return True

# Validate configuration on import
try:
    Config.validate_config()
    logger.info("Configuration module initialized successfully")
except Exception as e:
    logger.error(f"Configuration initialization failed: {e}")
    raise
