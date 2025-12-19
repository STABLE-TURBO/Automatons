import unittest
from unittest.mock import patch, MagicMock
import json
import hmac
import hashlib
from app import app, verify_github_webhook, generate_ai_content, post_to_linkedin, get_linkedin_person_urn

class TestAutomation(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.os.getenv')
    def test_verify_webhook_valid(self, mock_getenv):
        mock_getenv.return_value = 'test_secret'
        secret = 'test_secret'
        data = b'test data'
        hash_object = hmac.new(secret.encode(), msg=data, digestmod=hashlib.sha256)
        signature = "sha256=" + hash_object.hexdigest()
        self.assertTrue(verify_github_webhook(data, signature))

    @patch('app.os.getenv')
    def test_verify_webhook_invalid(self, mock_getenv):
        mock_getenv.return_value = 'test_secret'
        data = b'test data'
        signature = "sha256=invalid"
        self.assertFalse(verify_github_webhook(data, signature))

    @patch('app.OpenAI')
    @patch('app.os.getenv')
    def test_generate_ai_content(self, mock_getenv, mock_openai_class):
        mock_getenv.return_value = 'fake_key'
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_message = MagicMock()
        mock_message.content = "Test LinkedIn post"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = generate_ai_content('push', {'test': 'data'})
        self.assertEqual(result, "Test LinkedIn post")

    @patch('app.requests.get')
    def test_get_linkedin_person_urn(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': '12345'}
        mock_get.return_value = mock_response

        result = get_linkedin_person_urn()
        self.assertEqual(result, '12345')

    @patch('app.requests.get')
    def test_get_linkedin_person_urn_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = get_linkedin_person_urn()
        self.assertIsNone(result)

    @patch('app.get_linkedin_person_urn')
    @patch('app.requests.post')
    def test_post_to_linkedin_success(self, mock_post, mock_get_urn):
        mock_get_urn.return_value = '12345'
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        result = post_to_linkedin("Test content")
        self.assertTrue(result)

    @patch('app.get_linkedin_person_urn')
    @patch('app.requests.post')
    def test_post_to_linkedin_failure(self, mock_post, mock_get_urn):
        mock_get_urn.return_value = '12345'
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = post_to_linkedin("Test content")
        self.assertFalse(result)

    @patch('app.os.getenv')
    @patch('app.generate_ai_content')
    @patch('app.post_to_linkedin')
    def test_webhook_push_event(self, mock_post, mock_generate, mock_getenv):
        mock_getenv.side_effect = lambda key: 'test_secret' if key == 'GITHUB_WEBHOOK_SECRET' else 'fake_token'
        mock_generate.return_value = "AI generated content"
        mock_post.return_value = True

        payload = {'ref': 'refs/heads/main', 'commits': [{'message': 'Test commit'}]}
        data = json.dumps(payload).encode()
        signature = "sha256=" + hmac.new(b'test_secret', msg=data, digestmod=hashlib.sha256).hexdigest()

        response = self.app.post('/webhook',
                               data=data,
                               headers={
                                   'X-GitHub-Event': 'push',
                                   'X-Hub-Signature-256': signature,
                                   'Content-Type': 'application/json'
                               })

        self.assertEqual(response.status_code, 200)
        mock_generate.assert_called_once()
        mock_post.assert_called_once_with("AI generated content")

    @patch('app.os.getenv')
    @patch('app.generate_ai_content')
    @patch('app.post_to_linkedin')
    def test_webhook_unsupported_event(self, mock_post, mock_generate, mock_getenv):
        mock_getenv.side_effect = lambda key: 'test_secret' if key == 'GITHUB_WEBHOOK_SECRET' else 'fake_token'
        payload = {}
        data = json.dumps(payload).encode()
        signature = "sha256=" + hmac.new(b'test_secret', msg=data, digestmod=hashlib.sha256).hexdigest()

        response = self.app.post('/webhook',
                               data=data,
                               headers={
                                   'X-GitHub-Event': 'ping',
                                   'X-Hub-Signature-256': signature,
                                   'Content-Type': 'application/json'
                               })

        self.assertEqual(response.status_code, 200)
        mock_generate.assert_not_called()
        mock_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
