"""Gmail to LINE notification module."""

import base64
import json
import os
import pickle
from typing import Any

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from .config import AppConfig


class GmailNotifier:
	"""Gmail notification handler."""

	def __init__(
		self,
		oauth_credentials_json: str | None = None,
		token_file: str = 'token.pickle',
		oauth_token: str | None = None,
	):
		"""Initialize Gmail service with OAuth 2.0 credentials."""
		if oauth_token:
			# Use pre-generated token (for GitHub Actions)
			self.credentials = self._load_token_from_string(oauth_token)
		else:
			# Use interactive OAuth flow (for local development)
			self.credentials = self._get_oauth_credentials(oauth_credentials_json, token_file)
		self.service = build('gmail', 'v1', credentials=self.credentials)

	def _load_token_from_string(self, token_string: str) -> Credentials:
		"""Load credentials from base64 encoded token string."""
		import base64

		token_data = base64.b64decode(token_string.encode('utf-8'))
		return pickle.loads(token_data)  # type: ignore[no-any-return]

	def _get_oauth_credentials(self, oauth_credentials_json: str | None, token_file: str) -> Credentials:
		"""Get or refresh OAuth 2.0 credentials."""
		creds = None
		scopes = ['https://www.googleapis.com/auth/gmail.modify']

		# Load existing token
		if os.path.exists(token_file):
			with open(token_file, 'rb') as token:
				creds = pickle.load(token)

		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				# Parse OAuth credentials from JSON string or file path
				if not oauth_credentials_json:
					raise ValueError('oauth_credentials_json is required for initial authentication')

				if oauth_credentials_json.startswith('{'):
					# Direct JSON string
					creds_info = json.loads(oauth_credentials_json)
				else:
					# File path
					with open(oauth_credentials_json) as f:
						creds_info = json.load(f)

				flow = Flow.from_client_config(creds_info, scopes)
				flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # For desktop apps

				# Get authorization URL
				auth_url, _ = flow.authorization_url(prompt='consent')
				print(f'Please visit this URL to authorize the application: {auth_url}')

				# Get authorization code from user
				auth_code = input('Enter the authorization code: ')
				flow.fetch_token(code=auth_code)
				creds = flow.credentials

			# Save the credentials for the next run
			with open(token_file, 'wb') as token:
				pickle.dump(creds, token)

		return creds  # type: ignore[no-any-return]

	def get_unread_family_package_emails(
		self, user_id: str = 'me', label: str = 'Family/お荷物滞留お知らせメール'
	) -> dict[str, Any] | None:
		"""Fetch unread emails with specified label."""
		try:
			query = f'label:"{label}" is:unread'
			results = self.service.users().messages().list(userId=user_id, q=query, maxResults=1).execute()

			messages = results.get('messages', [])
			if not messages:
				print(f"No unread emails with '{label}' label found.")
				return None

			# Get details of the first message
			msg_id = messages[0]['id']
			message = self.service.users().messages().get(userId=user_id, id=msg_id).execute()

			return message  # type: ignore[no-any-return]

		except Exception as e:
			print(f'Error fetching emails: {str(e)}')
			raise

	def extract_email_content(self, message: dict[str, Any]) -> dict[str, str]:
		"""Extract email content from message."""
		headers = message['payload'].get('headers', [])
		subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
		from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

		body = self._extract_body(message['payload'])

		return {
			'id': message['id'],
			'subject': subject,
			'from': from_email,
			'body': body[:500] if body else 'No body content',  # First 500 characters
		}

	def _extract_body(self, payload: dict[str, Any]) -> str:
		"""Extract body text from email payload."""
		body = ''

		if 'parts' in payload:
			for part in payload['parts']:
				if part['mimeType'] == 'text/plain':
					data = part['body']['data']
					body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
		elif payload['body'].get('data'):
			body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')

		return body.strip()

	def mark_as_read(self, msg_id: str, user_id: str = 'me') -> None:
		"""Mark email as read."""
		try:
			self.service.users().messages().modify(
				userId=user_id, id=msg_id, body={'removeLabelIds': ['UNREAD']}
			).execute()
			print(f'Email {msg_id} marked as read')
		except Exception as e:
			print(f'Error marking email as read: {str(e)}')


class LineNotifier:
	"""LINE notification handler."""

	def __init__(self, channel_access_token: str, user_id: str):
		"""Initialize LINE notifier."""
		self.channel_access_token = channel_access_token
		self.user_id = user_id

	def send_notification(self, email_content: dict[str, str]) -> None:
		"""Send email notification to LINE."""
		url = 'https://api.line.me/v2/bot/message/push'
		headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.channel_access_token}'}

		message_text = '📧 新着メール (お荷物滞留お知らせ)\n\n'
		message_text += f'件名: {email_content["subject"]}\n'
		message_text += f'差出人: {email_content["from"]}\n\n'
		message_text += f'本文:\n{email_content["body"]}'

		data = {'to': self.user_id, 'messages': [{'type': 'text', 'text': message_text}]}

		response = requests.post(url, headers=headers, json=data)
		response.raise_for_status()
		print(f'LINE notification sent successfully for email: {email_content["id"]}')


class SlackNotifier:
	"""Slack notification handler."""

	def __init__(self, bot_token: str, channel_id: str):
		"""Initialize Slack notifier."""
		self.bot_token = bot_token
		self.channel_id = channel_id

	def send_error_notification(self, message: str) -> None:
		"""Send error notification to Slack."""
		url = 'https://slack.com/api/chat.postMessage'
		headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.bot_token}'}

		data = {'channel': self.channel_id, 'text': f'⚠️ Gmail to LINE Notification Failed\n\n{message}', 'mrkdwn': True}

		response = requests.post(url, headers=headers, json=data)
		response_data = response.json()

		if not response_data.get('ok'):
			print(f'Failed to send Slack notification: {response_data.get("error")}')
		else:
			print('Slack notification sent successfully')


def main() -> None:
	"""Main function to process Gmail notifications."""
	try:
		# Load configuration
		config = AppConfig.from_env()
		print(config.get_mode_display())

		# Initialize services
		gmail_notifier = GmailNotifier(
			oauth_credentials_json=config.google.oauth_credentials, oauth_token=config.google.oauth_token
		)
		line_notifier = LineNotifier(config.line.channel_access_token, config.line.user_id)

		# Check for unread emails
		message = gmail_notifier.get_unread_family_package_emails(label=config.gmail_label)

		if message:
			email_content = gmail_notifier.extract_email_content(message)

			# Add sandbox prefix to notification if in sandbox mode
			if config.sandbox_mode:
				email_content['subject'] = f'[SANDBOX] {email_content["subject"]}'

			line_notifier.send_notification(email_content)
			gmail_notifier.mark_as_read(email_content['id'])

			status_msg = f'success{config.get_status_suffix()}'
			with open(config.github_output_file, 'a') as f:
				f.write(f'status={status_msg}\n')
		else:
			print('No new emails to process')
			status_msg = f'no_emails{config.get_status_suffix()}'
			with open(config.github_output_file, 'a') as f:
				f.write(f'status={status_msg}\n')

	except Exception as e:
		print(f'Error in main process: {str(e)}')
		try:
			config = AppConfig.from_env()
			status_msg = f'failed{config.get_status_suffix()}'
			with open(config.github_output_file, 'a') as f:
				f.write(f'status={status_msg}\n')
		except Exception:
			# Fallback if config loading fails
			with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
				f.write('status=failed\n')
		raise


if __name__ == '__main__':
	main()
