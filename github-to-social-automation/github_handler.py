"""
GitHub Handler module for processing webhook events.

This module handles GitHub webhook verification and event processing.
"""

import hmac
import hashlib
import logging
from typing import Dict, Any
from config import Config
from event_manager import EventManager

logger = logging.getLogger(__name__)

class GitHubHandler:
    """Handles GitHub webhook events and verification."""

    @staticmethod
    def verify_webhook_signature(data: bytes, signature: str) -> bool:
        """
        Verify the GitHub webhook signature for security.

        Args:
            data (bytes): Raw request data
            signature (str): X-Hub-Signature-256 header value

        Returns:
            bool: True if signature is valid, False otherwise
        """
        if not Config.GITHUB_WEBHOOK_SECRET:
            logger.warning("GitHub webhook secret not configured")
            return False

        secret = Config.GITHUB_WEBHOOK_SECRET.encode()
        hash_object = hmac.new(secret, msg=data, digestmod=hashlib.sha256)
        expected_signature = "sha256=" + hash_object.hexdigest()

        is_valid = hmac.compare_digest(expected_signature, signature)
        if not is_valid:
            logger.warning("Invalid GitHub webhook signature")

        return is_valid

    @staticmethod
    def process_webhook_event(event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Process a GitHub webhook event by saving it for later summarization.

        Args:
            event_type (str): Type of GitHub event (push, release, etc.)
            payload (dict): Event payload from GitHub

        Returns:
            bool: True if event was processed successfully
        """
        supported_events = ['push', 'release', 'repository', 'organization']

        if event_type not in supported_events:
            logger.info(f"Ignoring unsupported event type: {event_type}")
            return False

        try:
            EventManager.save_event(event_type, payload)
            logger.info(f"Processed {event_type} event")
            return True
        except Exception as e:
            logger.error(f"Error processing {event_type} event: {e}")
            return False

    @staticmethod
    def get_supported_events() -> list:
        """
        Get list of supported GitHub event types.

        Returns:
            list: List of supported event type strings
        """
        return ['push', 'release', 'repository', 'organization']
