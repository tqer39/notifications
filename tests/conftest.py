"""pytestの共通設定とフィクスチャ"""

import os
import tempfile
from unittest.mock import patch
import pytest

from tests.fixtures.mock_data import get_mock_env_vars


@pytest.fixture
def mock_env_vars():
	"""テスト用環境変数をセットアップ"""
	test_env = get_mock_env_vars()
	with patch.dict(os.environ, test_env):
		yield test_env


@pytest.fixture
def temp_github_output():
	"""一時的なGITHUB_OUTPUTファイルを作成"""
	with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
		original_output = os.environ.get('GITHUB_OUTPUT')
		os.environ['GITHUB_OUTPUT'] = f.name
		yield f.name

		# クリーンアップ
		if original_output:
			os.environ['GITHUB_OUTPUT'] = original_output
		elif 'GITHUB_OUTPUT' in os.environ:
			del os.environ['GITHUB_OUTPUT']

		try:
			os.unlink(f.name)
		except FileNotFoundError:
			pass


@pytest.fixture
def mock_gmail_service():
	"""Gmail APIサービスのモック"""
	with patch('src.gmail_notifier.service_account.Credentials'), \
		 patch('src.gmail_notifier.build') as mock_build:

		yield mock_build


@pytest.fixture
def mock_requests():
	"""requestsモジュールのモック"""
	with patch('requests.post') as mock_post:
		yield mock_post
