"""Tests for gmail_notifier module."""

import base64
import json
from unittest.mock import Mock, patch

import responses

from src.gmail_notifier import GmailNotifier, LineNotifier, SlackNotifier


class TestGmailNotifier:
	"""Tests for GmailNotifier class."""

	@patch('src.gmail_notifier.build')
	@patch('src.gmail_notifier.pickle')
	def test_init_with_oauth_token(self, mock_pickle, mock_build):
		"""Test GmailNotifier initialization with OAuth token."""
		# Mock OAuth token
		mock_creds = Mock()
		mock_pickle.loads.return_value = mock_creds

		oauth_token = base64.b64encode(b'test_token').decode('utf-8')
		GmailNotifier(oauth_token=oauth_token)

		mock_pickle.loads.assert_called_once()
		mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

	@patch('src.gmail_notifier.build')
	@patch('src.gmail_notifier.pickle')
	def test_get_unread_fts_emails_no_messages(self, mock_pickle, mock_build):
		"""Test get_unread_fts_emails when no messages found."""
		mock_service = Mock()
		mock_build.return_value = mock_service
		mock_service.users().messages().list().execute.return_value = {'messages': []}

		credentials_json = json.dumps({'test': 'credentials'})
		notifier = GmailNotifier(credentials_json)

		result = notifier.get_unread_fts_emails()

		assert result is None
		mock_service.users().messages().list.assert_called_once_with(userId='me', q='label:fts is:unread', maxResults=1)

	@patch('src.gmail_notifier.build')
	@patch('src.gmail_notifier.service_account.Credentials')
	def test_get_unread_fts_emails_with_message(self, mock_credentials, mock_build):
		"""Test get_unread_fts_emails when message is found."""
		mock_service = Mock()
		mock_build.return_value = mock_service

		# Mock list response
		mock_service.users().messages().list().execute.return_value = {'messages': [{'id': 'test_id'}]}

		# Mock get response
		expected_message = {'id': 'test_id', 'payload': {'headers': []}}
		mock_service.users().messages().get().execute.return_value = expected_message

		credentials_json = json.dumps({'test': 'credentials'})
		notifier = GmailNotifier(credentials_json)

		result = notifier.get_unread_fts_emails()

		assert result == expected_message
		mock_service.users().messages().get.assert_called_once_with(userId='me', id='test_id')

	def test_extract_email_content(self):
		"""Test extract_email_content method."""
		message = {
			'id': 'test_id',
			'payload': {
				'headers': [
					{'name': 'Subject', 'value': 'Test Subject'},
					{'name': 'From', 'value': 'test@example.com'},
				],
				'body': {'data': base64.urlsafe_b64encode(b'Test body content').decode()},
			},
		}

		notifier = GmailNotifier.__new__(GmailNotifier)
		result = notifier.extract_email_content(message)

		assert result['id'] == 'test_id'
		assert result['subject'] == 'Test Subject'
		assert result['from'] == 'test@example.com'
		assert result['body'] == 'Test body content'

	def test_extract_body_with_parts(self):
		"""Test _extract_body with multipart message."""
		payload = {
			'parts': [
				{'mimeType': 'text/plain', 'body': {'data': base64.urlsafe_b64encode(b'Part 1').decode()}},
				{'mimeType': 'text/html', 'body': {'data': base64.urlsafe_b64encode(b'<html>Part 2</html>').decode()}},
				{'mimeType': 'text/plain', 'body': {'data': base64.urlsafe_b64encode(b' Part 3').decode()}},
			]
		}

		notifier = GmailNotifier.__new__(GmailNotifier)
		result = notifier._extract_body(payload)

		assert result == 'Part 1 Part 3'

	@patch('src.gmail_notifier.build')
	@patch('src.gmail_notifier.service_account.Credentials')
	def test_mark_as_read(self, mock_credentials, mock_build):
		"""Test mark_as_read method."""
		mock_service = Mock()
		mock_build.return_value = mock_service

		credentials_json = json.dumps({'test': 'credentials'})
		notifier = GmailNotifier(credentials_json)

		notifier.mark_as_read('test_id')

		mock_service.users().messages().modify.assert_called_once_with(
			userId='me', id='test_id', body={'removeLabelIds': ['UNREAD']}
		)


class TestLineNotifier:
	"""Tests for LineNotifier class."""

	def test_init(self):
		"""Test LineNotifier initialization."""
		notifier = LineNotifier('test_token', 'test_user_id')
		assert notifier.channel_access_token == 'test_token'
		assert notifier.user_id == 'test_user_id'

	@responses.activate
	def test_send_notification(self):
		"""Test send_notification method."""
		responses.add(responses.POST, 'https://api.line.me/v2/bot/message/push', json={'message': 'ok'}, status=200)

		notifier = LineNotifier('test_token', 'test_user_id')
		email_content = {'id': 'test_id', 'subject': 'Test Subject', 'from': 'test@example.com', 'body': 'Test body'}

		notifier.send_notification(email_content)

		assert len(responses.calls) == 1
		request = responses.calls[0].request
		assert request.headers['Authorization'] == 'Bearer test_token'
		assert request.headers['Content-Type'] == 'application/json'

		body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
		body = json.loads(body_str) if body_str else {}
		assert body['to'] == 'test_user_id'
		assert len(body['messages']) == 1
		assert body['messages'][0]['type'] == 'text'
		assert 'Test Subject' in body['messages'][0]['text']
		assert 'test@example.com' in body['messages'][0]['text']
		assert 'Test body' in body['messages'][0]['text']


class TestSlackNotifier:
	"""Tests for SlackNotifier class."""

	def test_init(self):
		"""Test SlackNotifier initialization."""
		notifier = SlackNotifier('test_token', 'test_channel')
		assert notifier.bot_token == 'test_token'
		assert notifier.channel_id == 'test_channel'

	@responses.activate
	def test_send_error_notification_success(self):
		"""Test send_error_notification with successful response."""
		responses.add(responses.POST, 'https://slack.com/api/chat.postMessage', json={'ok': True}, status=200)

		notifier = SlackNotifier('test_token', 'test_channel')
		notifier.send_error_notification('Test error message')

		assert len(responses.calls) == 1
		request = responses.calls[0].request
		assert request.headers['Authorization'] == 'Bearer test_token'

		body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
		body = json.loads(body_str) if body_str else {}
		assert body['channel'] == 'test_channel'
		assert 'Test error message' in body['text']
		assert body['mrkdwn'] is True

	@responses.activate
	def test_send_error_notification_failure(self):
		"""Test send_error_notification with failed response."""
		responses.add(
			responses.POST,
			'https://slack.com/api/chat.postMessage',
			json={'ok': False, 'error': 'invalid_auth'},
			status=200,
		)

		notifier = SlackNotifier('test_token', 'test_channel')
		notifier.send_error_notification('Test error message')

		assert len(responses.calls) == 1
