"""Gmail to LINE notification module."""

import os
import json
import base64
from typing import Optional, Dict, Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests


class GmailNotifier:
	"""Gmail notification handler."""

	def __init__(self, credentials_json: str):
		"""Initialize Gmail service with credentials."""
		creds_info = json.loads(credentials_json)
		self.credentials = service_account.Credentials.from_service_account_info(
			creds_info,
			scopes=['https://www.googleapis.com/auth/gmail.readonly']
		)
		self.service = build('gmail', 'v1', credentials=self.credentials)

	def get_unread_fts_emails(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
		"""Fetch unread emails with 'fts' label."""
		try:
			query = 'label:fts is:unread'
			results = self.service.users().messages().list(
				userId=user_id,
				q=query,
				maxResults=1
			).execute()

			messages = results.get('messages', [])
			if not messages:
				print("No unread emails with 'fts' label found.")
				return None

			# Get details of the first message
			msg_id = messages[0]['id']
			message = self.service.users().messages().get(
				userId=user_id,
				id=msg_id
			).execute()

			return message

		except Exception as e:
			print(f"Error fetching emails: {str(e)}")
			raise

	def extract_email_content(self, message: Dict[str, Any]) -> Dict[str, str]:
		"""Extract email content from message."""
		headers = message['payload'].get('headers', [])
		subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
		from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

		body = self._extract_body(message['payload'])

		return {
			'id': message['id'],
			'subject': subject,
			'from': from_email,
			'body': body[:500] if body else 'No body content'  # First 500 characters
		}

	def _extract_body(self, payload: Dict[str, Any]) -> str:
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
				userId=user_id,
				id=msg_id,
				body={'removeLabelIds': ['UNREAD']}
			).execute()
			print(f"Email {msg_id} marked as read")
		except Exception as e:
			print(f"Error marking email as read: {str(e)}")


class LineNotifier:
	"""LINE notification handler."""

	def __init__(self, channel_access_token: str, user_id: str):
		"""Initialize LINE notifier."""
		self.channel_access_token = channel_access_token
		self.user_id = user_id

	def send_notification(self, email_content: Dict[str, str]) -> None:
		"""Send email notification to LINE."""
		url = 'https://api.line.me/v2/bot/message/push'
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f"Bearer {self.channel_access_token}"
		}

		message_text = f"📧 新着メール (ftsラベル)\n\n"
		message_text += f"件名: {email_content['subject']}\n"
		message_text += f"差出人: {email_content['from']}\n\n"
		message_text += f"本文:\n{email_content['body']}"

		data = {
			'to': self.user_id,
			'messages': [
				{
					'type': 'text',
					'text': message_text
				}
			]
		}

		response = requests.post(url, headers=headers, json=data)
		response.raise_for_status()
		print(f"LINE notification sent successfully for email: {email_content['id']}")


class SlackNotifier:
	"""Slack notification handler."""

	def __init__(self, bot_token: str, channel_id: str):
		"""Initialize Slack notifier."""
		self.bot_token = bot_token
		self.channel_id = channel_id

	def send_error_notification(self, message: str) -> None:
		"""Send error notification to Slack."""
		url = 'https://slack.com/api/chat.postMessage'
		headers = {
			'Content-Type': 'application/json',
			'Authorization': f"Bearer {self.bot_token}"
		}

		data = {
			'channel': self.channel_id,
			'text': f"⚠️ Gmail to LINE Notification Failed\n\n{message}",
			'mrkdwn': True
		}

		response = requests.post(url, headers=headers, json=data)
		response_data = response.json()

		if not response_data.get('ok'):
			print(f"Failed to send Slack notification: {response_data.get('error')}")
		else:
			print("Slack notification sent successfully")


def main() -> None:
	"""Main function to process Gmail notifications."""
	try:
		# Initialize services
		gmail_notifier = GmailNotifier(os.environ['GOOGLE_CREDENTIALS'])
		line_notifier = LineNotifier(
			os.environ['LINE_CHANNEL_ACCESS_TOKEN'],
			os.environ['LINE_USER_ID']
		)

		# Check for unread emails
		message = gmail_notifier.get_unread_fts_emails()

		if message:
			email_content = gmail_notifier.extract_email_content(message)
			line_notifier.send_notification(email_content)
			gmail_notifier.mark_as_read(email_content['id'])
			with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
				f.write('status=success\n')
		else:
			print("No new emails to process")
			with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
				f.write('status=no_emails\n')

	except Exception as e:
		print(f"Error in main process: {str(e)}")
		with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
			f.write('status=failed\n')
		raise


if __name__ == '__main__':
	main()
