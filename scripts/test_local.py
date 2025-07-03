#!/usr/bin/env python3
"""ローカルテスト用スクリプト"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gmail_notifier import GmailNotifier, LineNotifier, SlackNotifier  # noqa: E402


def load_test_env() -> None:
	"""テスト用環境変数を読み込み"""
	env_file = project_root / '.env.test'
	if not env_file.exists():
		print('❌ .env.testファイルが見つかりません')
		print('📝 .env.exampleを参考に.env.testを作成してください')
		sys.exit(1)

	with open(env_file) as f:
		for line in f:
			line = line.strip()
			if line and not line.startswith('#'):
				key, value = line.split('=', 1)
				os.environ[key] = value
	print('✅ テスト用環境変数を読み込みました')


def test_gmail_notifier() -> Optional[Dict[str, Any]]:
	"""Gmail通知のテスト"""
	print('\n🔍 Gmail通知のテスト開始...')

	# モックサービスを作成
	with patch('src.gmail_notifier.pickle'), patch('src.gmail_notifier.build') as mock_build:
		mock_service = MagicMock()
		mock_build.return_value = mock_service

		# モックレスポンス設定
		mock_service.users().messages().list().execute.return_value = {'messages': [{'id': 'test_message_id'}]}

		# モックメッセージ設定
		mock_message = {
			'id': 'test_message_id',
			'payload': {
				'headers': [
					{'name': 'Subject', 'value': 'テストメール件名'},
					{'name': 'From', 'value': 'test@example.com'},
				],
				'body': {
					'data': 'VGVzdCBib2R5IGNvbnRlbnQ='  # base64 encoded "Test body content"
				},
			},
		}
		mock_service.users().messages().get().execute.return_value = mock_message

		# テスト実行
		notifier = GmailNotifier(oauth_token=os.environ.get('GOOGLE_OAUTH_TOKEN'))
		message = notifier.get_unread_family_package_emails()

		if message:
			email_content = notifier.extract_email_content(message)
			print('✅ メール取得成功:')
			print(f'   📧 件名: {email_content["subject"]}')
			print(f'   👤 差出人: {email_content["from"]}')
			print(f'   📝 本文: {email_content["body"][:50]}...')
			return email_content
		else:
			print('⚠️  未読メールなし')
			return None


def test_line_notifier(email_content: Dict[str, Any]) -> None:
	"""LINE通知のテスト"""
	print('\n📱 LINE通知のテスト開始...')

	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.raise_for_status.return_value = None
		mock_post.return_value = mock_response

		notifier = LineNotifier(os.environ['LINE_CHANNEL_ACCESS_TOKEN'], os.environ['LINE_USER_ID'])

		notifier.send_notification(email_content)

		# リクエスト内容確認
		assert mock_post.called
		call_args = mock_post.call_args

		print('✅ LINE通知送信成功')
		print(f'   🔗 URL: {call_args[0][0] if call_args[0] else "https://api.line.me/v2/bot/message/push"}')
		print(f'   📋 データ: {json.dumps(call_args.kwargs.get("json", {}), ensure_ascii=False, indent=2)}')


def test_slack_notifier() -> None:
	"""Slack通知のテスト"""
	print('\n💬 Slack通知のテスト開始...')

	with patch('requests.post') as mock_post:
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = {'ok': True}
		mock_post.return_value = mock_response

		notifier = SlackNotifier(os.environ['SLACK_BOT_TOKEN'], os.environ['SLACK_CHANNEL_ID'])

		test_message = 'テストエラーメッセージ'
		notifier.send_error_notification(test_message)

		# リクエスト内容確認
		assert mock_post.called
		call_args = mock_post.call_args

		print('✅ Slack通知送信成功')
		print(f'   🔗 URL: {call_args[0][0] if call_args[0] else "https://slack.com/api/chat.postMessage"}')
		print(f'   📋 データ: {json.dumps(call_args.kwargs.get("json", {}), ensure_ascii=False, indent=2)}')


def test_main_workflow() -> None:
	"""メインワークフローのテスト"""
	print('\n🔄 メインワークフロー統合テスト...')

	# 一時ファイルでGITHUB_OUTPUTをテスト
	with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
		os.environ['GITHUB_OUTPUT'] = f.name

		with (
			patch('src.gmail_notifier.pickle'),
			patch('src.gmail_notifier.build') as mock_build,
			patch('requests.post') as mock_post,
		):
			# Gmail APIモック
			mock_service = MagicMock()
			mock_build.return_value = mock_service
			mock_service.users().messages().list().execute.return_value = {'messages': [{'id': 'test_id'}]}
			mock_service.users().messages().get().execute.return_value = {
				'id': 'test_id',
				'payload': {
					'headers': [
						{'name': 'Subject', 'value': 'Integration Test'},
						{'name': 'From', 'value': 'test@example.com'},
					],
					'body': {'data': 'VGVzdCBtZXNzYWdl'},  # "Test message"
				},
			}

			# LINE APIモック
			mock_response = MagicMock()
			mock_response.raise_for_status.return_value = None
			mock_post.return_value = mock_response

			# メイン関数実行
			from src.gmail_notifier import main

			main()

			# GITHUB_OUTPUT確認
			with open(f.name) as output_f:
				output = output_f.read()
				if 'status=success' in output:
					print('✅ メインワークフロー成功')
				else:
					print(f'⚠️  予期しない出力: {output}')

		# 一時ファイル削除
		os.unlink(f.name)


def main() -> None:
	"""メインテスト関数"""
	print('🧪 ローカルテスト開始')
	print('=' * 50)

	try:
		# 環境変数読み込み
		load_test_env()

		# Gmail通知テスト
		email_content = test_gmail_notifier()

		if email_content:
			# LINE通知テスト
			test_line_notifier(email_content)
		else:
			# テスト用のダミーデータ
			email_content = {
				'id': 'dummy_id',
				'subject': 'ダミーテスト件名',
				'from': 'dummy@example.com',
				'body': 'ダミーテスト本文',
			}
			test_line_notifier(email_content)

		# Slack通知テスト
		test_slack_notifier()

		# 統合テスト
		test_main_workflow()

		print('\n' + '=' * 50)
		print('🎉 すべてのテストが完了しました！')

	except Exception as e:
		print(f'\n❌ テスト中にエラーが発生しました: {e}')
		import traceback

		traceback.print_exc()
		sys.exit(1)


if __name__ == '__main__':
	main()
