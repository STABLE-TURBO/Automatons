# GitHub-to-Social AI Automation

This application automates posting to LinkedIn about GitHub events using AI-generated content.

## Features

- Monitors GitHub webhooks for releases, commits (pushes), repository changes, and organization events
- Uses OpenAI GPT to generate engaging LinkedIn posts
- Automatically posts to LinkedIn

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env` and fill in your API keys and tokens:
   - `GITHUB_TOKEN`: Personal access token with repo and webhook permissions
   - `GITHUB_WEBHOOK_SECRET`: Secret for webhook verification
   - `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME`: If monitoring specific repo
   - `LINKEDIN_ACCESS_TOKEN`: LinkedIn access token
   - `OPENAI_API_KEY`: OpenAI API key
4. Run the application: `python app.py`
5. Set up GitHub webhooks pointing to your server URL + `/webhook`

## LinkedIn Setup

To get LinkedIn access token:
1. Create a LinkedIn app at https://developer.linkedin.com/
2. Get client ID and secret
3. Use OAuth 2.0 to get access token
4. Get your person URN from LinkedIn API

## GitHub Webhook Events

Configure webhooks for:
- Push (for commits)
- Release (for releases)
- Repository (for repo changes)
- Organization (for org changes)

## Note

This is a basic implementation. For production use, consider:
- Error handling and retries
- Rate limiting
- Logging
- Security improvements
