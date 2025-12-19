"""Unit tests for event_manager module."""

import pytest
import json
import os
from unittest.mock import patch, mock_open
from event_manager import EventManager


class TestEventManager:
    """Test cases for EventManager class."""

    def test_summarize_event_push(self):
        """Test summarizing push events."""
        payload = {
            'commits': [{'message': 'Add new feature'}],
            'ref': 'refs/heads/main'
        }
        summary = EventManager.summarize_event('push', payload)
        assert 'push' in summary.lower()
        assert 'main' in summary

    def test_summarize_event_release(self):
        """Test summarizing release events."""
        payload = {
            'release': {'tag_name': 'v1.0.0'},
            'repository': {'name': 'test-repo'}
        }
        summary = EventManager.summarize_event('release', payload)
        assert 'release' in summary.lower() or 'v1.0.0' in summary

    def test_summarize_event_unknown(self):
        """Test summarizing unknown events."""
        payload = {'some': 'data'}
        summary = EventManager.summarize_event('unknown', payload)
        assert 'unknown' in summary.lower()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('json.dump')
    def test_save_event(self, mock_json_dump, mock_exists, mock_file):
        """Test saving events."""
        mock_exists.return_value = False

        EventManager.save_event('push', {'test': 'data'})

        # Should call open and json.dump
        mock_file.assert_called()
        mock_json_dump.assert_called()

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.exists')
    @patch('json.load')
    def test_load_events(self, mock_json_load, mock_exists, mock_file):
        """Test loading events."""
        mock_exists.return_value = True
        mock_json_load.return_value = [{'type': 'push'}]

        events = EventManager.load_events()
        assert isinstance(events, list)

    @patch('os.rename')
    @patch('os.path.exists')
    def test_archive_events(self, mock_exists, mock_rename):
        """Test archiving events."""
        mock_exists.return_value = True

        EventManager.archive_events()

        # Should call rename if file exists
        mock_rename.assert_called()
