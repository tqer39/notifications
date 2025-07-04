"""Tests for config module."""

import os
from unittest.mock import patch

import pytest

from src.config import AppConfig, GoogleConfig, LineConfig, SlackConfig


class TestGoogleConfig:
	"""Tests for GoogleConfig."""

	@patch.dict(os.environ, {'GOOGLE_OAUTH_TOKEN': 'test_token', 'GOOGLE_OAUTH_CREDENTIALS': 'test_creds'})
	def test_from_env_with_values(self):
		"""Test GoogleConfig.from_env with environment variables set."""
		config = GoogleConfig.from_env()
		assert config.oauth_token == 'test_token'
		assert config.oauth_credentials == 'test_creds'

	@patch.dict(os.environ, {}, clear=True)
	def test_from_env_without_values(self):
		"""Test GoogleConfig.from_env without environment variables."""
		config = GoogleConfig.from_env()
		assert config.oauth_token is None
		assert config.oauth_credentials is None


class TestLineConfig:
	"""Tests for LineConfig."""

	@patch.dict(
		os.environ,
		{
			'LINE_CHANNEL_ACCESS_TOKEN': 'prod_token',
			'LINE_USER_ID': 'prod_user',
			'LINE_CHANNEL_ACCESS_TOKEN_SANDBOX': 'sandbox_token',
			'LINE_USER_ID_SANDBOX': 'sandbox_user',
		}
	)
	def test_from_env_production_mode(self):
		"""Test LineConfig.from_env in production mode."""
		config = LineConfig.from_env(sandbox_mode=False)
		assert config.channel_access_token == 'prod_token'
		assert config.user_id == 'prod_user'

	@patch.dict(
		os.environ,
		{
			'LINE_CHANNEL_ACCESS_TOKEN': 'prod_token',
			'LINE_USER_ID': 'prod_user',
			'LINE_CHANNEL_ACCESS_TOKEN_SANDBOX': 'sandbox_token',
			'LINE_USER_ID_SANDBOX': 'sandbox_user',
		}
	)
	def test_from_env_sandbox_mode(self):
		"""Test LineConfig.from_env in sandbox mode."""
		config = LineConfig.from_env(sandbox_mode=True)
		assert config.channel_access_token == 'sandbox_token'
		assert config.user_id == 'sandbox_user'

	@patch.dict(os.environ, {}, clear=True)
	def test_from_env_missing_production_token(self):
		"""Test LineConfig.from_env with missing production token."""
		with pytest.raises(ValueError, match='Environment variable LINE_CHANNEL_ACCESS_TOKEN is required'):
			LineConfig.from_env(sandbox_mode=False)

	@patch.dict(os.environ, {'LINE_CHANNEL_ACCESS_TOKEN': 'token'}, clear=True)
	def test_from_env_missing_production_user_id(self):
		"""Test LineConfig.from_env with missing production user ID."""
		with pytest.raises(ValueError, match='Environment variable LINE_USER_ID is required'):
			LineConfig.from_env(sandbox_mode=False)


class TestSlackConfig:
	"""Tests for SlackConfig."""

	@patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'test_token', 'SLACK_CHANNEL_ID': 'test_channel'})
	def test_from_env_with_values(self):
		"""Test SlackConfig.from_env with environment variables set."""
		config = SlackConfig.from_env()
		assert config.bot_token == 'test_token'
		assert config.channel_id == 'test_channel'

	@patch.dict(os.environ, {}, clear=True)
	def test_from_env_missing_token(self):
		"""Test SlackConfig.from_env with missing bot token."""
		with pytest.raises(ValueError, match='Environment variable SLACK_BOT_TOKEN is required'):
			SlackConfig.from_env()

	@patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'token'}, clear=True)
	def test_from_env_missing_channel_id(self):
		"""Test SlackConfig.from_env with missing channel ID."""
		with pytest.raises(ValueError, match='Environment variable SLACK_CHANNEL_ID is required'):
			SlackConfig.from_env()


class TestAppConfig:
	"""Tests for AppConfig."""

	@patch.dict(
		os.environ,
		{
			'SANDBOX_MODE': 'false',
			'GITHUB_OUTPUT': '/tmp/output',
			'LINE_CHANNEL_ACCESS_TOKEN': 'prod_token',
			'LINE_USER_ID': 'prod_user',
			'SLACK_BOT_TOKEN': 'slack_token',
			'SLACK_CHANNEL_ID': 'slack_channel',
		}
	)
	def test_from_env_production_mode(self):
		"""Test AppConfig.from_env in production mode."""
		config = AppConfig.from_env()
		assert config.sandbox_mode is False
		assert config.github_output_file == '/tmp/output'
		assert config.gmail_label == 'Family/お荷物滞留お知らせメール'
		assert config.line.channel_access_token == 'prod_token'
		assert config.line.user_id == 'prod_user'

	@patch.dict(
		os.environ,
		{
			'SANDBOX_MODE': 'true',
			'LINE_CHANNEL_ACCESS_TOKEN_SANDBOX': 'sandbox_token',
			'LINE_USER_ID_SANDBOX': 'sandbox_user',
			'SLACK_BOT_TOKEN': 'slack_token',
			'SLACK_CHANNEL_ID': 'slack_channel',
		},
		clear=True,
	)
	def test_from_env_sandbox_mode(self):
		"""Test AppConfig.from_env in sandbox mode."""
		config = AppConfig.from_env()
		assert config.sandbox_mode is True
		assert config.github_output_file == '/dev/null'  # default value
		assert config.line.channel_access_token == 'sandbox_token'
		assert config.line.user_id == 'sandbox_user'

	@patch.dict(
		os.environ,
		{
			'SANDBOX_MODE': 'false',
			'LINE_CHANNEL_ACCESS_TOKEN': 'token',
			'LINE_USER_ID': 'user',
			'SLACK_BOT_TOKEN': 'slack_token',
			'SLACK_CHANNEL_ID': 'slack_channel',
		}
	)
	def test_get_status_suffix_production(self):
		"""Test get_status_suffix in production mode."""
		config = AppConfig.from_env()
		assert config.get_status_suffix() == ''

	@patch.dict(
		os.environ,
		{
			'SANDBOX_MODE': 'true',
			'LINE_CHANNEL_ACCESS_TOKEN_SANDBOX': 'token',
			'LINE_USER_ID_SANDBOX': 'user',
			'SLACK_BOT_TOKEN': 'slack_token',
			'SLACK_CHANNEL_ID': 'slack_channel',
		}
	)
	def test_get_status_suffix_sandbox(self):
		"""Test get_status_suffix in sandbox mode."""
		config = AppConfig.from_env()
		assert config.get_status_suffix() == '_sandbox'

	@patch.dict(
		os.environ,
		{
			'SANDBOX_MODE': 'false',
			'LINE_CHANNEL_ACCESS_TOKEN': 'token',
			'LINE_USER_ID': 'user',
			'SLACK_BOT_TOKEN': 'slack_token',
			'SLACK_CHANNEL_ID': 'slack_channel',
		}
	)
	def test_get_mode_display_production(self):
		"""Test get_mode_display in production mode."""
		config = AppConfig.from_env()
		assert config.get_mode_display() == '🚀 Running in PRODUCTION mode'

	@patch.dict(
		os.environ,
		{
			'SANDBOX_MODE': 'true',
			'LINE_CHANNEL_ACCESS_TOKEN_SANDBOX': 'token',
			'LINE_USER_ID_SANDBOX': 'user',
			'SLACK_BOT_TOKEN': 'slack_token',
			'SLACK_CHANNEL_ID': 'slack_channel',
		}
	)
	def test_get_mode_display_sandbox(self):
		"""Test get_mode_display in sandbox mode."""
		config = AppConfig.from_env()
		assert config.get_mode_display() == '🧪 Running in SANDBOX mode'
