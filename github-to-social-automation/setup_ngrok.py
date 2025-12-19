#!/usr/bin/env python3
"""
Ngrok Setup Helper Script

This script helps you set up ngrok for webhook testing when you don't have a server.
Run this after installing ngrok and getting your authtoken.
"""

import subprocess
import time
import requests
import os

def check_ngrok_installation():
    """Check if ngrok is installed."""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            print(f"Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ ngrok not found. Please install from https://ngrok.com/download")
            return False
    except FileNotFoundError:
        print("❌ ngrok not found. Please install from https://ngrok.com/download")
        return False

def setup_ngrok_authtoken():
    """Guide user to set up ngrok authtoken."""
    print("\n🔑 Ngrok Auth Token Setup:")
    print("1. Go to https://dashboard.ngrok.com/get-started/your-authtoken")
    print("2. Copy your authtoken")
    print("3. Run: ngrok config add-authtoken YOUR_TOKEN_HERE")
    print("\nExample:")
    print("ngrok config add-authtoken 2abcd...xyz")
    print("\nThis gives you persistent URLs and longer session times.")

def start_flask_app():
    """Start the Flask app in background."""
    print("\n🐍 Starting Flask app on port 5000...")

    try:
        # Start Flask app in background
        process = subprocess.Popen(['python', 'app.py'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        # Wait for Flask to start up
        time.sleep(3)

        # Check for any immediate errors
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("❌ Flask app failed to start")
            if stderr:
                print(f"Error output: {stderr}")
            if stdout:
                print(f"Standard output: {stdout}")
            return None

        # Wait a bit more
        time.sleep(5)

        # Test if Flask is responding
        try:
            response = requests.get('http://localhost:5000/health', timeout=5)
            if response.status_code == 200:
                print("✅ Flask app is running successfully!")
                return process
            else:
                print(f"⚠️  Flask app returned status {response.status_code}")
                # Get response text for debugging
                try:
                    error_text = response.text
                    print(f"Response: {error_text}")
                except Exception:
                    pass
                return None
        except requests.RequestException as e:
            print("❌ Flask app not responding on localhost:5000")
            print(f"Connection error: {e}")
            print("\n🔍 Debugging steps:")
            print("1. Check if port 5000 is already in use: netstat -ano | findstr :5000")
            print("2. Try running 'python app.py' manually to see error messages")
            print("3. Check if all required environment variables are set in .env")
            print("4. Make sure all dependencies are installed: pip install -r requirements.txt")
            return None

    except FileNotFoundError:
        print("❌ Could not start Flask app")
        print("Make sure 'python' command is available and app.py exists")
        return None
    except Exception as e:
        print(f"❌ Unexpected error starting Flask app: {e}")
        return None

def start_ngrok_tunnel():
    """Start ngrok tunnel on port 5000."""
    print("\n🚀 Starting ngrok tunnel on port 5000...")

    try:
        # Start ngrok in background
        process = subprocess.Popen(['ngrok', 'http', '5000'],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

        # Wait a moment for ngrok to start
        time.sleep(5)

        # Get ngrok status
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                for tunnel in tunnels:
                    if tunnel['proto'] == 'https':
                        url = tunnel['public_url']
                        print("\n🎉 ngrok tunnel active!")
                        print(f"🌐 Public URL: {url}")
                        print(f"🎯 Webhook URL: {url}/webhook")
                        print("\n📋 Copy this webhook URL to your GitHub webhook settings:")
                        print(f"   {url}/webhook")
                        return url, process
        except requests.RequestException:
            pass

        print("❌ Could not get ngrok tunnel URL")
        print("Troubleshooting:")
        print("1. Make sure ngrok is installed and authenticated")
        print("2. Check if port 5000 is in use by another application")
        print("3. Try running: ngrok http 5000 manually")
        return None, None

    except FileNotFoundError:
        print("❌ ngrok command not found")
        print("Please install ngrok from https://ngrok.com/download")
        return None, None

def test_webhook_endpoint(url):
    """Test if the webhook endpoint is responding."""
    if not url:
        return

    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Webhook endpoint is responding!")
            data = response.json()
            print(f"Status: {data.get('status', 'unknown')}")
        else:
            print(f"⚠️  Webhook endpoint returned status {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Could not reach webhook endpoint: {e}")
        print("Make sure your Flask app is running: python app.py")

def create_sample_env():
    """Create a sample .env file if it doesn't exist."""
    if os.path.exists('.env'):
        print("ℹ️  .env file already exists")
        return

    sample_env = """# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_random_secret_string

# LinkedIn Configuration
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Groq Configuration (Free!)
GROQ_API_KEY=your_groq_api_key_here

# Optional: Change daily post time (UTC)
DAILY_POST_TIME=18:00"""

    with open('.env', 'w') as f:
        f.write(sample_env)

    print("📝 Created sample .env file")
    print("⚠️  Please fill in your actual API keys and tokens")

def main():
    """Main setup function."""
    print("🔧 GitHub-to-Social Automation - ngrok Setup Helper")
    print("=" * 50)

    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")

    # Check if .env exists
    create_sample_env()

    # Check ngrok installation
    if not check_ngrok_installation():
        return

    # Guide for authtoken
    setup_ngrok_authtoken()

    # Start Flask app automatically
    flask_process = start_flask_app()
    if not flask_process:
        print("\n❌ Failed to start Flask app. Please check the errors above.")
        return

    # Start ngrok tunnel
    ngrok_url, ngrok_process = start_ngrok_tunnel()

    if ngrok_url:
        # Test the endpoint
        test_webhook_endpoint(ngrok_url)

        print("\n📋 Next Steps:")
        print("1. Copy the webhook URL above")
        print("2. Go to GitHub → Organization Settings → Webhooks")
        print("3. Add webhook with the URL above")
        print("4. Set content type to 'application/json'")
        print("5. Use your GITHUB_WEBHOOK_SECRET as the secret")
        print("6. Test by making a commit!")

        print("\n🔄 Both Flask and ngrok are running in the background.")
        print("Keep this terminal open. Press Ctrl+C to stop everything.")

        try:
            # Keep the script running to maintain processes
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            if flask_process:
                flask_process.terminate()
            if ngrok_process:
                ngrok_process.terminate()
            print("✅ Shutdown complete")

    else:
        print("\n❌ Failed to start ngrok tunnel. Please check the errors above.")
        if flask_process:
            flask_process.terminate()

if __name__ == "__main__":
    main()
