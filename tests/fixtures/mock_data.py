"""テスト用のモックデータ"""

import base64
import json
from typing import Dict, Any


# Gmail APIモックデータ
MOCK_GMAIL_MESSAGE = {
	'id': 'mock_message_id_12345',
	'payload': {
		'headers': [
			{'name': 'Subject', 'value': 'テスト: 重要な通知'},
			{'name': 'From', 'value': 'important@example.com'},
			{'name': 'Date', 'value': 'Mon, 1 Jan 2024 12:00:00 +0900'},
		],
		'body': {
			'data': base64.urlsafe_b64encode(
				'これはテスト用のメール本文です。\n\n'
				'重要な情報が含まれています。\n'
				'確認をお願いします。'
			.encode('utf-8')).decode()
		}
	}
}

MOCK_GMAIL_MULTIPART_MESSAGE = {
	'id': 'mock_multipart_id_67890',
	'payload': {
		'headers': [
			{'name': 'Subject', 'value': 'マルチパートテストメール'},
			{'name': 'From', 'value': 'multipart@example.com'},
		],
		'parts': [
			{
				'mimeType': 'text/plain',
				'body': {
					'data': base64.urlsafe_b64encode(
						'プレーンテキスト部分です。'
					.encode('utf-8')).decode()
				}
			},
			{
				'mimeType': 'text/html',
				'body': {
					'data': base64.urlsafe_b64encode(
						'<html><body>HTML部分です。</body></html>'
					.encode('utf-8')).decode()
				}
			},
			{
				'mimeType': 'text/plain',
				'body': {
					'data': base64.urlsafe_b64encode(
						' 追加のプレーンテキスト。'
					.encode('utf-8')).decode()
				}
			}
		]
	}
}

# Gmail API レスポンスモック
MOCK_GMAIL_LIST_RESPONSE = {
	'messages': [
		{'id': 'mock_message_id_12345'},
		{'id': 'mock_message_id_67890'}
	]
}

MOCK_GMAIL_NO_MESSAGES_RESPONSE = {
	'messages': []
}

# LINE API モックデータ
MOCK_LINE_SUCCESS_RESPONSE = {
	'message': 'ok'
}

MOCK_LINE_ERROR_RESPONSE = {
	'message': 'Invalid channel access token'
}

# Slack API モックデータ
MOCK_SLACK_SUCCESS_RESPONSE = {
	'ok': True,
	'channel': 'C1234567890',
	'ts': '1234567890.123456'
}

MOCK_SLACK_ERROR_RESPONSE = {
	'ok': False,
	'error': 'channel_not_found'
}

# テスト用認証情報
MOCK_GOOGLE_CREDENTIALS = json.dumps({
	'type': 'service_account',
	'project_id': 'test-project-12345',
	'private_key_id': 'test-private-key-id',
	'private_key': '-----BEGIN RSA PRIVATE KEY-----\nTEST_RSA_PRIVATE_KEY_CONTENT\n-----END RSA PRIVATE KEY-----\n',
	'client_email': 'test-service@test-project-12345.iam.gserviceaccount.com',
	'client_id': '123456789012345678901',
	'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
	'token_uri': 'https://oauth2.googleapis.com/token',
	'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
	'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/test-service%40test-project-12345.iam.gserviceaccount.com'
})

# 期待される変換結果
EXPECTED_EMAIL_CONTENT = {
	'id': 'mock_message_id_12345',
	'subject': 'テスト: 重要な通知',
	'from': 'important@example.com',
	'body': 'これはテスト用のメール本文です。\n\n重要な情報が含まれています。\n確認をお願いします。'
}

EXPECTED_MULTIPART_BODY = 'プレーンテキスト部分です。 追加のプレーンテキスト。'


def get_mock_env_vars() -> Dict[str, str]:
	"""テスト用環境変数を取得"""
	return {
		'GOOGLE_CREDENTIALS': MOCK_GOOGLE_CREDENTIALS,
		'LINE_CHANNEL_ACCESS_TOKEN': 'test_line_channel_token',
		'LINE_USER_ID': 'U1234567890abcdef',
		'SLACK_BOT_TOKEN': 'xoxb-test-slack-bot-token',
		'SLACK_CHANNEL_ID': 'C1234567890',
		'GITHUB_OUTPUT': '/tmp/test_github_output',
		'GITHUB_REPOSITORY': 'test-user/test-repo',
		'GITHUB_RUN_ID': '987654321'
	}


def create_test_email_content(
	subject: str = "テストメール",
	from_email: str = "test@example.com",
	body: str = "テスト本文"
) -> Dict[str, str]:
	"""カスタムテスト用メールコンテンツを作成"""
	return {
		'id': 'custom_test_id',
		'subject': subject,
		'from': from_email,
		'body': body
	}
