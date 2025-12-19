"""
Scheduler module for daily automated posting.

This module handles the scheduling of daily LinkedIn posts.
"""

import logging
import schedule
import time
import threading
from datetime import datetime
from config import Config
from ai_processor import ai_processor
from event_manager import EventManager
from linkedin_poster import linkedin_poster

logger = logging.getLogger(__name__)

class DailyScheduler:
    """Handles scheduling of daily summary posts."""

    def __init__(self):
        """Initialize the scheduler."""
        self.is_running = False

    def check_for_missed_posts(self) -> None:
        """
        Check for missed posts from previous days and attempt to post them.
        This handles cases where the computer was shut down during posting time.
        """
        from datetime import datetime, timedelta
        import os

        logger.info("🔍 Checking for missed posts from previous days...")

        # Check last 7 days for unposted events
        for days_back in range(1, 8):
            check_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            events_file = f'events_{check_date}.json'
            posted_file = f'posted_events_{check_date}.json'

            # If events file exists but no posted file, we missed a post
            if os.path.exists(events_file) and not os.path.exists(posted_file):
                logger.warning(f"📅 Found missed post for {check_date}")
                logger.info(f"🔄 Attempting to post missed summary for {check_date}")

                try:
                    # Load the missed events
                    events = EventManager.load_events(check_date)

                    if events:
                        # Generate and post the missed summary
                        summary_content = ai_processor.generate_daily_summary(events)
                        success = linkedin_poster.review_and_post(summary_content)

                        if success:
                            EventManager.archive_events(check_date)
                            logger.info(f"✅ Successfully posted missed summary for {check_date}")
                        else:
                            logger.error(f"❌ Failed to post missed summary for {check_date}")
                    else:
                        logger.info(f"ℹ️  No events found for {check_date}")

                except Exception as e:
                    logger.error(f"💥 Error processing missed post for {check_date}: {e}")
            elif os.path.exists(posted_file):
                logger.debug(f"✅ {check_date} already posted")

    def _load_and_validate_events(self) -> list:
        """Load and validate today's events."""
        events = EventManager.load_events()
        logger.info(f"📊 Found {len(events)} events to summarize")

        if not events:
            logger.info("📭 No events to summarize for today")
            return []

        # Log event details
        event_types = {}
        for event in events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        logger.info(f"📈 Event breakdown: {event_types}")

        return events

    def _generate_ai_summary(self, events: list) -> str:
        """Generate AI summary for events."""
        logger.info("🤖 Generating AI summary...")
        summary_content = ai_processor.generate_daily_summary(events)
        logger.info("✅ AI summary generated successfully")
        logger.info(f"📝 Summary preview: {summary_content[:150]}...")
        return summary_content

    def _post_summary(self, summary_content: str, events: list) -> bool:
        """Post the summary using configured method."""
        posting_method = "Pipedream" if Config.USE_PIPEDREAM else "LinkedIn"
        logger.info(f"🔗 Posting to {posting_method}...")
        return linkedin_poster.review_and_post(summary_content, events)

    def _handle_posting_result(self, success: bool, events_count: int) -> None:
        """Handle the result of posting attempt."""
        if success:
            EventManager.archive_events()
            logger.info("🎉 Daily summary posted and events archived successfully!")
            logger.info(f"📊 Summary: {events_count} events processed, posted to LinkedIn")
        else:
            logger.error("❌ Failed to post daily summary to LinkedIn")
            logger.warning("💡 Events file not archived - will retry tomorrow")

    def post_daily_summary(self) -> None:
        """
        Generate and post daily summary of GitHub events.
        Called automatically by the scheduler.
        """
        logger.info("🚀 Starting daily summary post process")

        # First, check for any missed posts
        self.check_for_missed_posts()

        try:
            # Load and validate events
            events = self._load_and_validate_events()
            if not events:
                return

            # Generate AI summary
            summary_content = self._generate_ai_summary(events)

            # Post summary
            success = self._post_summary(summary_content, events)

            # Handle result
            self._handle_posting_result(success, len(events))

        except Exception as e:
            logger.error(f"💥 Error in daily summary process: {e}")
            logger.exception("Full error traceback:")

    def start_scheduler(self) -> None:
        """
        Start the daily scheduler.
        This runs in a separate thread and schedules posts at the configured time.
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        self.is_running = True
        schedule_time = Config.DAILY_POST_TIME

        logger.info(f"Starting daily scheduler - posts at {schedule_time} UTC")

        # Schedule the daily post
        schedule.every().day.at(schedule_time).do(self.post_daily_summary)

        # Run the scheduler loop
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait before retrying

        logger.info("Scheduler stopped")

    def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        logger.info("Stopping scheduler")
        self.is_running = False

    def run_in_thread(self) -> threading.Thread:
        """
        Start the scheduler in a background thread.

        Returns:
            threading.Thread: The scheduler thread
        """
        scheduler_thread = threading.Thread(
            target=self.start_scheduler,
            daemon=True,
            name="DailyScheduler"
        )
        scheduler_thread.start()
        logger.info("Scheduler started in background thread")
        return scheduler_thread

# Global instance
daily_scheduler = DailyScheduler()
