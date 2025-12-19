# GitHub-to-Social AI Automation

This application automates posting daily summaries to LinkedIn about GitHub events using AI-generated, humanized content.

## Features

- Monitors GitHub webhooks for releases, commits (pushes), repository changes, and organization events
- Accumulates events throughout the day and posts a single daily summary at 6 PM UTC
- Uses Groq (free LLM) to generate and humanize engaging LinkedIn posts
- Automatically posts to LinkedIn
- **Comprehensive Logging**: Every action logged with detailed information
- **Review System**: Manual approval required before posting (configurable)
- **Auto-Recovery**: Handles missed posts when computer shuts down
- **Auto-Startup**: Windows batch script for automatic launch on boot
- **Modular Architecture**: 8 well-documented modules for maintainability

## Is Groq Free?

Yes! Groq offers a generous free tier:
- **Free Credits**: New users get free credits to start
- **Mixtral Model**: Uses the free Mixtral-8x7B model
- **Rate Limits**: Reasonable limits for personal use
- **No Credit Card Required**: Sign up at https://console.groq.com/

## Step-by-Step Setup Guide

### 1. Clone and Install
```bash
git clone <your-repo-url>
cd github-social-automation
pip install -r requirements.txt
```

### 2. Get Groq API Key (Free)
1. Go to https://console.groq.com/
2. Sign up for a free account
3. Create an API key
4. Copy the API key

### 3. Get GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with these permissions:
   - `repo` (Full control of private repositories)
   - `admin:repo_hook` (for webhooks)
   - `admin:org_hook` (for organization webhooks)
   - `read:org` (for organization info)
3. Copy the token

**Note**: For organization-wide monitoring, ensure the token has access to the organization and all repositories you want to monitor.

### 4. Set Up LinkedIn API Access

**Option A: Automated Setup (Recommended)**
```bash
# First, fix the redirect URI to match your LinkedIn app
python fix_linkedin_redirect.py

# Then get your access token
python linkedin_oauth_helper.py
```

**What these scripts do:**
1. **`fix_linkedin_redirect.py`**: Updates the redirect URI to match your LinkedIn app settings
2. **`linkedin_oauth_helper.py`**: Opens browser, handles OAuth flow, gives you the access token

**Option B: Manual Setup**
1. Go to https://developer.linkedin.com/
2. Create a new app with these settings:
   - App name: "GitHub Social Automation"
   - LinkedIn page: Select your personal/company page
   - App logo: Upload any image
3. In "Auth" tab:
   - Redirect URLs: `http://localhost:8000/callback`
   - Scopes: `w_member_social` (for posting)
4. Copy Client ID and Client Secret to `.env`
5. Use OAuth tool or Postman to get access token

**Option C: Use Existing Token**
If you already have a LinkedIn access token, just paste it in `.env`

**Option D: Pipedream Integration (Easiest & Most Reliable)**
**Skip all LinkedIn OAuth complications!** Use Pipedream for serverless LinkedIn posting:

1. **Sign up at https://pipedream.com/** (free)
2. **Create workflow**: HTTP Trigger → LinkedIn Post
3. **Copy the Pipedream webhook URL**
4. **Your automation sends content** to Pipedream
5. **Pipedream handles LinkedIn posting** automatically

**See detailed guide:** `pipedream_setup.md`

**Benefits:**
- ✅ **Zero server management**
- ✅ **No OAuth headaches**
- ✅ **Handles LinkedIn auth automatically**
- ✅ **1000 free requests/month**
- ✅ **Visual workflow builder**
- ✅ **Enterprise reliability**

### 5. Configure Environment Variables
Create a `.env` file:
```env
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_random_secret_string

# LinkedIn Configuration
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Groq Configuration (Free!)
GROQ_API_KEY=your_groq_api_key_here

# Optional: Change daily post time (UTC)
DAILY_POST_TIME=18:00
```

### 6. Generate Webhook Secret
Create a random secret for webhook security:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Use this as `GITHUB_WEBHOOK_SECRET`

### 7. Run the Application
```bash
python app.py
```
The app will start on http://localhost:5000

## 🚀 Hosting Options (If You Don't Have a Server)

Since webhooks require a publicly accessible endpoint, here are several options:

### Option 1: ngrok (Free, Quick Start)
**Best for testing and development**

1. **Install ngrok**: Download from https://ngrok.com/download
2. **Run your app**: `python app.py`
3. **Expose locally**: `ngrok http 5000`
4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)
5. **Use as Payload URL**: `https://abc123.ngrok.io/webhook`

**Note**: Free ngrok URLs change on restart. For production, use ngrok auth token.

### Option 2: GitHub Actions (Free, Recommended)
**Serverless deployment using GitHub's infrastructure**

1. **Create GitHub repository** for your automation
2. **Add workflow file** `.github/workflows/deploy.yml`:
```yaml
name: Deploy Webhook Handler
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Railway/Render/Vercel
      # Add deployment steps here
```

### Option 3: Free Cloud Hosting

#### Railway (Free tier available)
1. Sign up at https://railway.app
2. Connect GitHub repo
3. Deploy automatically
4. Get your domain (e.g., `your-app.railway.app`)
5. Use as Payload URL: `https://your-app.railway.app/webhook`

#### Render (Free tier)
1. Sign up at https://render.com
2. Create Web Service from GitHub repo
3. Deploy Flask app
4. Get your domain
5. Use as Payload URL

#### Vercel (Free for static/Python)
1. Sign up at https://vercel.com
2. Deploy from GitHub
3. Get your domain
4. Use as Payload URL

### Option 4: Local Development with Webhook Testing
**For testing without public access**

1. **Run locally**: `python app.py`
2. **Test webhooks** using GitHub's webhook delivery page
3. **Use tools** like webhook.site or ngrok for temporary testing

### Recommended Setup for Beginners (Easiest):
1. **Install ngrok** from https://ngrok.com/download
2. **Get ngrok auth token** from https://dashboard.ngrok.com/get-started/your-authtoken
3. **Run**: `ngrok config add-authtoken YOUR_TOKEN`
4. **Fill in your API keys** in the `.env` file
5. **Run the automated setup**: `python setup_ngrok.py`
6. **The script automatically**:
   - ✅ Starts your Flask app
   - ✅ Launches ngrok tunnel
   - ✅ Tests everything is working
   - ✅ Provides your webhook URL
   - ✅ Keeps everything running

**Alternative Manual Setup:**
1. **Install ngrok**
2. **Run your app locally**: `python app.py`
3. **Start ngrok**: `ngrok http 5000`
4. **Use ngrok URL** as payload URL in GitHub webhook
5. **Test** by making commits and checking webhook deliveries

### 8. Set Up GitHub Webhooks

#### For Organization-Wide Monitoring (Recommended):
1. Go to your GitHub Organization → Settings → Webhooks
2. Click "Add webhook"
3. **Payload URL**: `https://your-domain.com/webhook` (your server's webhook endpoint)
4. **Content type**: `application/json`
5. **Secret**: Use your `GITHUB_WEBHOOK_SECRET`
6. **Which events would you like to trigger this webhook?**: Select "Send me everything" or choose:
   - Push
   - Release
   - Repository
   - Organization
7. Click "Add webhook"

#### For Single Repository Monitoring:
1. Go to specific Repository → Settings → Webhooks
2. Follow same steps as above
3. This will only monitor the single repository

### 9. Test the Setup
- Make a commit/push to test GitHub webhooks
- Check http://localhost:5000/health for status
- Check http://localhost:5000/stats for event counts
- Wait for 6 PM UTC to see the daily summary post

## Scope: Single Repository vs Organization

### Single Repository Setup
- Monitors one specific repository
- Webhooks configured per repository
- Daily summary for that repository's activity

### Organization-Wide Setup (Recommended)
- Monitors ALL repositories in your organization
- Single webhook at organization level
- Aggregates activity from all repos into one daily summary
- More comprehensive overview of organizational activity

## What are Webhooks?

Webhooks are HTTP callbacks triggered by events. Instead of constantly polling for changes, GitHub sends an HTTP POST request to your server when events occur. Your application receives these events in real-time and processes them.

### What is a Payload URL?

The **Payload URL** is the webhook endpoint where GitHub sends HTTP POST requests containing event data. It's your server's URL that receives the webhook payloads.

Example: `https://your-server.com/webhook`

When you push code to GitHub, it sends a POST request to this URL with JSON data about the push event.

## Project Structure

```
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── ai_processor.py       # AI content generation (Groq)
├── event_manager.py      # Event storage and retrieval
├── linkedin_poster.py    # LinkedIn API integration
├── github_handler.py     # GitHub webhook processing
├── scheduler.py          # Daily posting scheduler
├── setup_ngrok.py       # Ngrok setup helper script
├── test.py              # Unit tests
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
└── README.md           # This file
```

## How It Works

1. **Event Collection**: GitHub sends webhook events → saved to daily JSON files
2. **Daily Processing**: At 6 PM UTC, AI generates summary from events
3. **Humanization**: Content is rewritten to sound natural and professional
4. **Posting**: Summary posted to LinkedIn automatically
5. **Archiving**: Events file archived after posting

## API Endpoints

- `POST /webhook` - Receives GitHub webhook events
- `GET /health` - Health check and configuration info
- `GET /stats` - Event statistics for today

## Troubleshooting

### ERR_NGROK_8012 Error
**"Traffic successfully made it to the ngrok agent, but the agent failed to establish a connection to the upstream web service"**

This means ngrok is working but your Flask app isn't running on localhost:5000.

**Solutions:**
1. **Make sure Flask app is running**: Run `python app.py` in another terminal first
2. **Check port availability**: Run `netstat -ano | findstr :5000` to see if port is in use
3. **Use the setup script**: Run `python setup_ngrok.py` which starts both automatically
4. **Change port**: Set `PORT=5001` in `.env` and update ngrok command to `ngrok http 5001`

### Other Common Issues
- **Webhook not working**: Check webhook delivery in GitHub settings
- **Posts not appearing**: Verify LinkedIn token permissions
- **AI errors**: Check Groq API key and credits
- **Port issues**: Change PORT in .env if 5000 is occupied
- **ngrok URLs change**: Get auth token for persistent URLs

## Production Deployment

For production use:
- Use a proper WSGI server (gunicorn)
- Set up HTTPS
- Use environment variables instead of .env file
- Set up monitoring and logging
- Configure firewall and security groups
