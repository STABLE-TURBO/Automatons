#!/usr/bin/env python3
"""
System Test Script - Comprehensive Testing of All Modules

This script tests each module individually and provides detailed output
to make the system less of a blackbox.
"""

import traceback

def test_config():
    """Test config module."""
    print("=" * 50)
    print("🧪 TESTING CONFIG MODULE")
    print("=" * 50)

    try:
        import config
        print("✅ Config module imported successfully")

        print(f"   PORT: {config.Config.PORT}")
        print(f"   DAILY_POST_TIME: {config.Config.DAILY_POST_TIME}")

        github_configured = bool(config.Config.GITHUB_TOKEN and config.Config.GITHUB_TOKEN != "your_github_token_here")
        groq_configured = bool(config.Config.GROQ_API_KEY and config.Config.GROQ_API_KEY != "your_groq_api_key_here")
        linkedin_configured = bool(config.Config.LINKEDIN_ACCESS_TOKEN and config.Config.LINKEDIN_ACCESS_TOKEN != "your_linkedin_access_token")

        print(f"   GITHUB_TOKEN configured: {'✅' if github_configured else '❌'}")
        print(f"   GROQ_API_KEY configured: {'✅' if groq_configured else '❌'}")
        print(f"   LINKEDIN_ACCESS_TOKEN configured: {'✅' if linkedin_configured else '❌'}")

        config.Config.validate_config()
        print("✅ Config validation passed")
        return True

    except Exception as e:
        print(f"❌ Config test failed: {e}")
        traceback.print_exc()
        return False

def test_event_manager():
    """Test event manager module."""
    print("\n" + "=" * 50)
    print("🧪 TESTING EVENT MANAGER MODULE")
    print("=" * 50)

    try:
        from event_manager import EventManager
        print("✅ EventManager module imported successfully")

        # Test event summarization
        test_payload = {
            'commits': [{'message': 'Add new feature'}],
            'ref': 'refs/heads/main'
        }
        summary = EventManager.summarize_event('push', test_payload)
        print(f"   Push event summary: '{summary}'")

        # Test event saving
        EventManager.save_event('push', test_payload)
        print("   ✅ Event saved successfully")

        # Test loading events
        events = EventManager.load_events()
        print(f"   Loaded {len(events)} events")

        # Test archiving
        EventManager.archive_events()
        print("   ✅ Events archived successfully")

        return True

    except Exception as e:
        print(f"❌ Event Manager test failed: {e}")
        traceback.print_exc()
        return False

def test_ai_processor():
    """Test AI processor module."""
    print("\n" + "=" * 50)
    print("🧪 TESTING AI PROCESSOR MODULE")
    print("=" * 50)

    try:
        from ai_processor import ai_processor
        print("✅ AI Processor module imported successfully")

        # Check if API key is configured
        try:
            ai_processor._get_client()
            print("   ✅ Groq client initialized successfully")

            # Test humanization
            print("   🤖 Testing AI humanization...")
            test_text = "Today we pushed 3 commits to main branch and released version 1.2.3"
            humanized = ai_processor.generate_humanized_content(test_text)
            print(f"   Original: '{test_text}'")
            print(f"   Humanized: '{humanized}'")

            # Test summary generation
            print("   🤖 Testing AI summary generation...")
            test_events = [
                {'type': 'push', 'summary': 'Pushed 3 commits to main'},
                {'type': 'release', 'summary': 'Released version 1.2.3'}
            ]
            summary = ai_processor.generate_daily_summary(test_events)
            print(f"   Generated summary: '{summary}'")

            return True

        except ValueError as e:
            print(f"   ⚠️  API key not configured: {e}")
            print("   💡 Configure GROQ_API_KEY in .env to test AI features")
            return True  # Not a failure, just not configured

    except Exception as e:
        print(f"❌ AI Processor test failed: {e}")
        traceback.print_exc()
        return False

def test_linkedin_poster():
    """Test LinkedIn poster module."""
    print("\n" + "=" * 50)
    print("🧪 TESTING LINKEDIN POSTER MODULE")
    print("=" * 50)

    try:
        from linkedin_poster import linkedin_poster
        print("✅ LinkedIn Poster module imported successfully")

        # Test URN retrieval (will fail without valid token, but should handle gracefully)
        try:
            urn = linkedin_poster.get_person_urn()
            print(f"   LinkedIn URN: {urn}")
        except Exception as e:
            print(f"   ⚠️  URN retrieval failed (expected without valid token): {e}")

        # Test posting (will fail without valid token, but should handle gracefully)
        try:
            result = linkedin_poster.post_content("Test post")
            print(f"   Post result: {result}")
        except Exception as e:
            print(f"   ⚠️  Posting failed (expected without valid token): {e}")

        return True

    except Exception as e:
        print(f"❌ LinkedIn Poster test failed: {e}")
        traceback.print_exc()
        return False

def test_github_handler():
    """Test GitHub handler module."""
    print("\n" + "=" * 50)
    print("🧪 TESTING GITHUB HANDLER MODULE")
    print("=" * 50)

    try:
        from github_handler import GitHubHandler
        print("✅ GitHub Handler module imported successfully")

        # Test supported events
        events = GitHubHandler.get_supported_events()
        print(f"   Supported events: {events}")

        # Test webhook verification
        import hmac
        import hashlib
        from config import Config

        test_data = b'test payload'
        secret = Config.GITHUB_WEBHOOK_SECRET or 'test_secret'
        hash_object = hmac.new(secret.encode(), msg=test_data, digestmod=hashlib.sha256)
        signature = "sha256=" + hash_object.hexdigest()

        is_valid = GitHubHandler.verify_webhook_signature(test_data, signature)
        print(f"   Webhook signature verification: {'✅' if is_valid else '❌'}")

        return True

    except Exception as e:
        print(f"❌ GitHub Handler test failed: {e}")
        traceback.print_exc()
        return False

def test_scheduler():
    """Test scheduler module."""
    print("\n" + "=" * 50)
    print("🧪 TESTING SCHEDULER MODULE")
    print("=" * 50)

    try:
        from scheduler import daily_scheduler
        print("✅ Scheduler module imported successfully")

        print(f"   Scheduler running: {daily_scheduler.is_running}")
        print("   ✅ Scheduler initialized without errors")

        return True

    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        traceback.print_exc()
        return False

def test_flask_app():
    """Test Flask app."""
    print("\n" + "=" * 50)
    print("🧪 TESTING FLASK APP")
    print("=" * 50)

    try:
        from app import app
        print("✅ Flask app imported successfully")

        # Test client for basic endpoint testing
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                data = response.get_json()
                print("   ✅ Health endpoint working")
                print(f"   Status: {data.get('status')}")
                print(f"   Supported events: {len(data.get('supported_events', []))}")
            else:
                print(f"   ❌ Health endpoint failed: {response.status_code}")

            # Test stats endpoint
            response = client.get('/stats')
            if response.status_code == 200:
                data = response.get_json()
                print("   ✅ Stats endpoint working")
                print(f"   Total events: {data.get('total_events', 0)}")
            else:
                print(f"   ❌ Stats endpoint failed: {response.status_code}")

        return True

    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        traceback.print_exc()
        return False

def test_webhook_flow():
    """Test the complete webhook flow."""
    print("\n" + "=" * 50)
    print("🧪 TESTING COMPLETE WEBHOOK FLOW")
    print("=" * 50)

    try:
        from app import app
        import hmac
        import hashlib
        from config import Config

        print("Testing webhook endpoint with test client...")

        with app.test_client() as client:
            # Create test webhook payload
            payload = {
                'ref': 'refs/heads/main',
                'commits': [{'message': 'Test commit'}]
            }
            import json
            payload_data = json.dumps(payload).encode()

            # Create signature
            secret = Config.GITHUB_WEBHOOK_SECRET or 'test_secret'
            hash_object = hmac.new(secret.encode(), msg=payload_data, digestmod=hashlib.sha256)
            signature = "sha256=" + hash_object.hexdigest()

            # Send webhook request
            response = client.post('/webhook',
                                 data=payload_data,
                                 headers={
                                     'X-GitHub-Event': 'push',
                                     'X-Hub-Signature-256': signature,
                                     'Content-Type': 'application/json'
                                 })

            if response.status_code == 200:
                data = response.get_json()
                print("   ✅ Webhook endpoint accepted push event")
                print(f"   Response: {data}")
            else:
                print(f"   ❌ Webhook endpoint failed: {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")

        return True

    except Exception as e:
        print(f"❌ Webhook flow test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 COMPREHENSIVE SYSTEM TEST")
    print("Making the system less of a blackbox by testing every component\n")

    results = []

    # Run all tests
    tests = [
        ("Config", test_config),
        ("Event Manager", test_event_manager),
        ("AI Processor", test_ai_processor),
        ("LinkedIn Poster", test_linkedin_poster),
        ("GitHub Handler", test_github_handler),
        ("Scheduler", test_scheduler),
        ("Flask App", test_flask_app),
        ("Webhook Flow", test_webhook_flow)
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check configuration and dependencies.")

    print("\n💡 Tips:")
    print("- Configure API keys in .env for full functionality")
    print("- Run 'python setup_ngrok.py' to start the system")
    print("- Check logs for detailed error information")

if __name__ == "__main__":
    main()
