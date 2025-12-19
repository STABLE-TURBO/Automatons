"""
GitHub-to-Social AI Automation - Main Application

This is the main Flask application that handles GitHub webhooks and coordinates
all components of the automation system.
"""

import logging
from flask import Flask, request, jsonify
from config import Config
from github_handler import GitHubHandler
from scheduler import daily_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """
    Handle GitHub webhook events.

    This endpoint receives webhook payloads from GitHub when configured events occur.
    Events are validated and stored for later summarization.
    """
    try:
        # Get raw request data and signature for verification
        data = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')

        # Verify webhook signature for security
        if not GitHubHandler.verify_webhook_signature(data, signature):
            logger.warning("Webhook signature verification failed")
            return jsonify({'error': 'Invalid signature'}), 403

        # Extract event type and payload
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.get_json()

        logger.info(f"Received GitHub webhook: {event_type}")

        # Process the webhook event
        if GitHubHandler.process_webhook_event(event_type, payload):
            return jsonify({'status': 'Event saved for daily summary'}), 200
        else:
            return jsonify({'status': 'Event not handled'}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns the status of the application and configuration.
    """
    return jsonify({
        'status': 'healthy',
        'supported_events': GitHubHandler.get_supported_events(),
        'daily_post_time': Config.DAILY_POST_TIME
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about stored events.

    Returns event counts and types for today.
    """
    from event_manager import EventManager
    stats = EventManager.get_event_stats()
    return jsonify(stats)

if __name__ == '__main__':
    logger.info("Starting GitHub-to-Social AI Automation")

    # Start the daily scheduler in a background thread
    scheduler_thread = daily_scheduler.run_in_thread()

    # Start the Flask web server
    logger.info(f"Starting web server on port {Config.PORT}")
    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=False  # Set to False for production
    )
