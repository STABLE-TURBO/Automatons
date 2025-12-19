"""
Event Manager module for handling GitHub event storage and retrieval.

This module manages the persistence of GitHub events to daily JSON files.
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EventManager:
    """Manages GitHub event storage and retrieval."""

    @staticmethod
    def summarize_event(event_type: str, payload: Dict[str, Any]) -> str:
        """
        Create a human-readable summary of a GitHub event.

        Args:
            event_type (str): Type of GitHub event (push, release, etc.)
            payload (dict): Event payload from GitHub webhook

        Returns:
            str: Summary of the event
        """
        # Extract repository name from payload
        repo_info = payload.get('repository', {})
        repo_name = repo_info.get('full_name') or repo_info.get('name') or 'unknown-repo'

        if event_type == 'push':
            commits = payload.get('commits', [])
            branch = payload.get('ref', '').replace('refs/heads/', '')
            return f"Pushed {len(commits)} commits to {branch} in {repo_name}"
        elif event_type == 'release':
            release = payload.get('release', {})
            tag = release.get('tag_name', 'unknown')
            return f"Released version {tag} in {repo_name}"
        elif event_type == 'repository':
            action = payload.get('action', 'updated')
            return f"Repository {action}: {repo_name}"
        elif event_type == 'organization':
            action = payload.get('action', 'updated')
            return f"Organization {action}"
        else:
            return f"{event_type} event occurred in {repo_name}"

    @staticmethod
    def save_event(event_type: str, payload: Dict[str, Any]) -> None:
        """
        Save a GitHub event to today's event file.

        Args:
            event_type (str): Type of GitHub event
            payload (dict): Full event payload
        """
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f'events_{date}.json'

        event_data = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'summary': EventManager.summarize_event(event_type, payload),
            'payload': payload  # Store full payload for potential future use
        }

        logger.info(f"📝 Processing {event_type} event: {event_data['summary']}")
        logger.debug(f"Full event payload: {json.dumps(payload, indent=2)}")

        # Load existing events or create new list
        events = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                logger.debug(f"Loaded {len(events)} existing events from {filename}")
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading existing events file {filename}: {e}")
                events = []

        # Add new event
        events.append(event_data)

        # Save back to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {event_type} event to {filename}. Total events today: {len(events)}")
        except IOError as e:
            logger.error(f"❌ Error saving event to {filename}: {e}")
            raise

    @staticmethod
    def load_events(date: str = None) -> List[Dict[str, Any]]:
        """
        Load events for a specific date.

        Args:
            date (str, optional): Date in YYYY-MM-DD format. Defaults to today.

        Returns:
            list: List of event dictionaries
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        filename = f'events_{date}.json'

        if not os.path.exists(filename):
            return []

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                events = json.load(f)
            return events
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading events from {filename}: {e}")
            return []

    @staticmethod
    def archive_events(date: str = None) -> bool:
        """
        Archive today's event file after posting.

        Args:
            date (str, optional): Date to archive. Defaults to today.

        Returns:
            bool: True if archived successfully, False otherwise
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        source_filename = f'events_{date}.json'
        archive_filename = f'posted_events_{date}.json'

        if not os.path.exists(source_filename):
            logger.warning(f"No events file to archive: {source_filename}")
            return False

        try:
            os.rename(source_filename, archive_filename)
            logger.info(f"Archived events file to {archive_filename}")
            return True
        except OSError as e:
            logger.error(f"Error archiving events file: {e}")
            return False

    @staticmethod
    def get_event_stats(date: str = None) -> Dict[str, int]:
        """
        Get statistics about events for a date.

        Args:
            date (str, optional): Date to analyze. Defaults to today.

        Returns:
            dict: Statistics about events
        """
        events = EventManager.load_events(date)

        stats = {
            'total_events': len(events),
            'event_types': {}
        }

        for event in events:
            event_type = event.get('type', 'unknown')
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1

        return stats
