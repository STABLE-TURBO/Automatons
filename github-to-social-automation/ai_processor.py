"""
AI Processor module for content generation and humanization.

This module handles all AI-related operations using Groq's LLM service.
"""

import logging
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

class AIProcessor:
    """Handles AI content generation and humanization using Groq."""

    def __init__(self):
        """Initialize the AI processor."""
        self.client = None
        self.model = "llama-3.1-8b-instant"  # Current stable free tier model

    def _get_client(self):
        """Get or create the Groq client."""
        if self.client is None:
            if not Config.GROQ_API_KEY or Config.GROQ_API_KEY == 'your_groq_api_key_here':
                error_msg = "Valid GROQ_API_KEY not configured. Please set it in your .env file."
                logger.error(error_msg)
                raise ValueError(error_msg)

            try:
                logger.info("Initializing Groq client...")
                self.client = Groq(api_key=Config.GROQ_API_KEY)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                # Try alternative initialization for compatibility
                try:
                    logger.info("Attempting alternative Groq initialization...")
                    # Fallback for httpx compatibility issues
                    import httpx
                    if hasattr(httpx, 'Client'):
                        # Force older httpx version behavior
                        self.client = Groq(api_key=Config.GROQ_API_KEY, http_client=httpx.Client())
                        logger.info("Groq client initialized with alternative method")
                    else:
                        raise e
                except Exception as e2:
                    logger.error(f"Alternative initialization also failed: {e2}")
                    raise e

        return self.client

    def generate_humanized_content(self, text: str) -> str:
        """
        Humanize AI-generated text to sound more natural and professional.

        Args:
            text (str): Raw AI-generated text

        Returns:
            str: Humanized version of the text
        """
        prompt = f"""Rewrite the following text to sound more natural and human-like,
as if written by a professional sharing on LinkedIn. Make it engaging and conversational:

{text}

Humanized version:"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error humanizing content: {e}")
            return text  # Return original text if humanization fails

    def generate_daily_summary(self, events: list) -> str:
        """
        Generate a daily summary post from a list of GitHub events.

        Args:
            events (list): List of event dictionaries with 'type' and 'summary'

        Returns:
            str: AI-generated summary post
        """
        # Create a readable list of events
        events_text = "\n".join([
            f"- {event['type'].title()}: {event['summary']}"
            for event in events
        ])

        prompt = f"""Generate a factual summary of GitHub events with commit details.

Input:
{events_text}

Output format:
- List specific actions performed with details
- Include actual commit messages and changes
- Use format: "X commits: [commit details]. PR #N: [PR title]. vX.X: [release notes]. Issue #N: [issue title]."
- No hashtags
- No conversational language
- Technical details only
- Under 250 characters

Example: "5 commits: updated AI models, fixed API calls, added error handling. PR #42: user authentication feature. v2.1.0: new performance improvements. Issue #15: resolved memory leak."

Summary:"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=400,
                temperature=0.8
            )
            raw_summary = response.choices[0].message.content.strip()
            # Return raw factual summary (no humanization for technical posts)
            return raw_summary
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            # Fallback summary
            total_events = len(events)
            event_types = [e['type'] for e in events]
            return f"Today we had {total_events} GitHub activities including {', '.join(set(event_types))}. Great progress on our projects!"

# Global instance for easy importing
ai_processor = AIProcessor()
