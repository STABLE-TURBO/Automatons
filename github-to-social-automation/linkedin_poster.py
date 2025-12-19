"""
LinkedIn Poster module for posting content to LinkedIn.

This module handles authentication and posting to LinkedIn via their API.
"""

import logging
import requests
import json
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class LinkedInPoster:
    """Handles posting content to LinkedIn."""

    def __init__(self):
        """Initialize with LinkedIn access token."""
        self.access_token = Config.LINKEDIN_ACCESS_TOKEN
        self.person_urn = None

    def get_person_urn(self) -> str:
        """
        Get the LinkedIn person URN for the authenticated user.

        Returns:
            str: Person URN (e.g., 'urn:li:person:123456789')

        Raises:
            ValueError: If unable to retrieve person URN
        """
        if self.person_urn:
            return self.person_urn

        # Try v3 API first (newer)
        url = "https://api.linkedin.com/v3/people/me"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            person_id = data.get('id')

            if person_id:
                self.person_urn = f"urn:li:person:{person_id}"
                logger.info("Retrieved LinkedIn person URN using v3 API")
                return self.person_urn

        except requests.RequestException as e:
            logger.warning(f"v3 API failed, trying v2: {e}")

        # Fallback to v2 API (deprecated but still works for some tokens)
        url_v2 = "https://api.linkedin.com/v2/people/~"
        try:
            response = requests.get(url_v2, headers={"Authorization": f"Bearer {self.access_token}"}, timeout=10)
            response.raise_for_status()

            data = response.json()
            person_id = data.get('id')

            if not person_id:
                raise ValueError("Person ID not found in LinkedIn response")

            self.person_urn = f"urn:li:person:{person_id}"
            logger.info("Retrieved LinkedIn person URN using v2 API")
            return self.person_urn

        except requests.RequestException as e:
            logger.error(f"Error retrieving LinkedIn person URN from both APIs: {e}")
            # For posting, we can try without person URN using organization URN
            # Let's try to get organization URN instead
            try:
                logger.info("Attempting to use organization URN for posting...")
                # This would require additional setup, for now return a placeholder
                raise ValueError("Unable to get person URN - token may lack required permissions")
            except:
                raise ValueError(f"Failed to get LinkedIn person URN: {e}")

    def post_content(self, content: str) -> bool:
        """
        Post content to LinkedIn.

        Args:
            content (str): Text content to post

        Returns:
            bool: True if posting succeeded, False otherwise
        """
        logger.info(f"🔗 Preparing to post to LinkedIn (length: {len(content)} chars)")
        logger.info(f"📝 Post content preview: {content[:100]}{'...' if len(content) > 100 else ''}")

        try:
            author_urn = self.get_person_urn()
            logger.debug(f"Using author URN: {author_urn}")

            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            logger.debug(f"LinkedIn API payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()

            logger.info("✅ Successfully posted to LinkedIn")
            logger.info(f"📊 Response status: {response.status_code}")

            # Log the post details for tracking
            post_id = response.headers.get('x-linkedin-id', 'unknown')
            logger.info(f"📋 LinkedIn post ID: {post_id}")
            logger.info(f"📅 Posted at: {datetime.now().isoformat()}")

            return True

        except requests.HTTPError as e:
            logger.error(f"❌ LinkedIn API error: {e.response.status_code} - {e.response.text}")
            return False
        except requests.RequestException as e:
            logger.error(f"❌ Network error posting to LinkedIn: {e}")
            return False
        except ValueError as e:
            logger.error(f"❌ Configuration error: {e}")
            return False

    def send_to_pipedream(self, content: str, events: list) -> bool:
        """
        Send content to Pipedream webhook instead of posting directly to LinkedIn.

        Args:
            content (str): The AI-generated content
            events (list): List of events for additional context

        Returns:
            bool: True if sent successfully, False otherwise
        """
        from config import Config

        payload = {
            "event_type": "daily_summary",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_events": len(events),
                "event_types": list(set(event['type'] for event in events))
            },
            "events_summary": [
                {
                    "type": event['type'],
                    "summary": event['summary'],
                    "timestamp": event['timestamp']
                } for event in events[:10]  # Include first 10 events for context
            ]
        }

        try:
            logger.info(f"📡 Sending to Pipedream: {Config.PIPEDREAM_WEBHOOK_URL}")
            response = requests.post(
                Config.PIPEDREAM_WEBHOOK_URL,
                json=payload,
                timeout=15
            )
            response.raise_for_status()

            logger.info("✅ Successfully sent to Pipedream")
            logger.info(f"📊 Response status: {response.status_code}")
            return True

        except requests.RequestException as e:
            logger.error(f"❌ Failed to send to Pipedream: {e}")
            return False

    def review_and_post(self, content: str, events: list = None) -> bool:
        """
        Review content before posting (if review is required).

        Args:
            content (str): Content to potentially post
            events (list): Event list for Pipedream context

        Returns:
            bool: True if posted (or approved), False otherwise
        """
        from config import Config

        if not Config.REQUIRE_POST_REVIEW:
            logger.info("🔄 Post review disabled, posting directly")
            if Config.USE_PIPEDREAM:
                return self.send_to_pipedream(content, events or [])
            else:
                return self.post_content(content)

        # Create review file
        review_file = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(review_file, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Post Review\n")
            f.write(f"Generated at: {datetime.now().isoformat()}\n")
            f.write(f"Content length: {len(content)} characters\n")
            f.write(f"Posting method: {'Pipedream' if Config.USE_PIPEDREAM else 'Direct LinkedIn'}\n")
            f.write(f"\n{'='*50}\n")
            f.write(f"{content}\n")
            f.write(f"{'='*50}\n")
            f.write(f"\nTo approve this post, edit this file and change 'APPROVE=false' to 'APPROVE=true'\n")
            f.write(f"APPROVE=false\n")

        logger.warning(f"⚠️  POST REVIEW REQUIRED!")
        logger.warning(f"📄 Review file created: {review_file}")
        logger.warning(f"📖 Please review the content and set APPROVE=true to post")
        logger.warning(f"🔄 The system will check for approval every 5 minutes")

        # Wait for approval
        import time
        max_attempts = 12  # 1 hour max wait
        attempts = 0

        while attempts < max_attempts:
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    if 'APPROVE=true' in file_content:
                        logger.info("✅ Post approved! Posting content...")

                        # Extract clean content (remove approval lines)
                        lines = file_content.split('\n')
                        content_lines = []
                        in_content = False
                        for line in lines:
                            if line.startswith('=') and not in_content:
                                in_content = True
                                continue
                            elif line.startswith('=') and in_content:
                                break
                            elif in_content and not line.startswith('APPROVE='):
                                content_lines.append(line)

                        clean_content = '\n'.join(content_lines).strip()

                        # Post using configured method
                        if Config.USE_PIPEDREAM:
                            success = self.send_to_pipedream(clean_content, events or [])
                        else:
                            success = self.post_content(clean_content)

                        # Archive review file
                        archive_file = f"posted_{review_file}"
                        import os
                        os.rename(review_file, archive_file)
                        logger.info(f"📁 Review file archived as: {archive_file}")

                        return success

                logger.info(f"⏳ Waiting for approval... (attempt {attempts + 1}/{max_attempts})")
                time.sleep(300)  # Wait 5 minutes
                attempts += 1

            except FileNotFoundError:
                logger.error(f"Review file {review_file} not found")
                return False

        logger.warning(f"⏰ Review timeout reached. Post not approved within 1 hour.")
        return False

# Global instance for easy importing
linkedin_poster = LinkedInPoster()
