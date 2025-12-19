import os
import hmac
import hashlib
import json
import logging
from flask import Flask, request, jsonify
from github import Github
from openai import OpenAI
import requests
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Initialize clients
github = Github(os.getenv('GITHUB_TOKEN'))
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')

def get_linkedin_person_urn():
    url = "https://api.linkedin.com/v2/people/~"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('id')
    return None

def verify_github_webhook(data, signature):
    secret = os.getenv('GITHUB_WEBHOOK_SECRET').encode()
    hash_object = hmac.new(secret, msg=data, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def generate_ai_content(event_type, event_data):
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    prompt = f"Generate an engaging LinkedIn post about this GitHub {event_type} event: {json.dumps(event_data, indent=2)}"
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

def post_to_linkedin(content):
    person_urn = get_linkedin_person_urn()
    if not person_urn:
        logging.error("Failed to get LinkedIn person URN")
        return False

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "author": f"urn:li:person:{person_urn}",
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
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 201

@app.route('/webhook', methods=['POST'])
def github_webhook():
    try:
        data = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')

        if not verify_github_webhook(data, signature):
            logging.warning("Invalid webhook signature")
            return jsonify({'error': 'Invalid signature'}), 403

        event = request.headers.get('X-GitHub-Event')
        payload = request.get_json()

        logging.info(f"Received GitHub webhook event: {event}")

        if event in ['push', 'release', 'repository', 'organization']:
            ai_content = generate_ai_content(event, payload)
            success = post_to_linkedin(ai_content)
            if success:
                logging.info("Successfully posted to LinkedIn")
                return jsonify({'status': 'Posted to LinkedIn'}), 200
            else:
                logging.error("Failed to post to LinkedIn")
                return jsonify({'error': 'Failed to post to LinkedIn'}), 500

        return jsonify({'status': 'Event not handled'}), 200
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
