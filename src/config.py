"""Configuration management for Gmail to LINE notification system."""

import os
from dataclasses import dataclass


@dataclass
class GoogleConfig:
	"""Google OAuth configuration."""

	oauth_token: str | None
	oauth_credentials: str | None

	@classmethod
	def from_env(cls) -> 'GoogleConfig':
		"""Create GoogleConfig from environment variables."""
		return cls(
			oauth_token=os.environ.get('GOOGLE_OAUTH_TOKEN'),
			oauth_credentials=os.environ.get('GOOGLE_OAUTH_CREDENTIALS'),
		)


@dataclass
class LineConfig:
	"""LINE Messaging API configuration."""

	channel_access_token: str
	user_id: str

	@classmethod
	def from_env(cls, sandbox_mode: bool = False) -> 'LineConfig':
		"""Create LineConfig from environment variables.

		Args:
			sandbox_mode: If True, use sandbox environment variables.
		"""
		if sandbox_mode:
			token_key = 'LINE_CHANNEL_ACCESS_TOKEN_SANDBOX'
			user_id_key = 'LINE_USER_ID_SANDBOX'
		else:
			token_key = 'LINE_CHANNEL_ACCESS_TOKEN'
			user_id_key = 'LINE_USER_ID'

		channel_access_token = os.environ.get(token_key)
		user_id = os.environ.get(user_id_key)

		if not channel_access_token:
			raise ValueError(f'Environment variable {token_key} is required')
		if not user_id:
			raise ValueError(f'Environment variable {user_id_key} is required')

		return cls(
			channel_access_token=channel_access_token,
			user_id=user_id,
		)


@dataclass
class SlackConfig:
	"""Slack API configuration."""

	bot_token: str
	channel_id: str

	@classmethod
	def from_env(cls) -> 'SlackConfig':
		"""Create SlackConfig from environment variables."""
		bot_token = os.environ.get('SLACK_BOT_TOKEN')
		channel_id = os.environ.get('SLACK_CHANNEL_ID')

		if not bot_token:
			raise ValueError('Environment variable SLACK_BOT_TOKEN is required')
		if not channel_id:
			raise ValueError('Environment variable SLACK_CHANNEL_ID is required')

		return cls(
			bot_token=bot_token,
			channel_id=channel_id,
		)


@dataclass
class AppConfig:
	"""Application configuration."""

	sandbox_mode: bool
	github_output_file: str
	gmail_label: str

	google: GoogleConfig
	line: LineConfig
	slack: SlackConfig

	@classmethod
	def from_env(cls) -> 'AppConfig':
		"""Create AppConfig from environment variables."""
		sandbox_mode = os.environ.get('SANDBOX_MODE', 'false').lower() == 'true'

		return cls(
			sandbox_mode=sandbox_mode,
			github_output_file=os.environ.get('GITHUB_OUTPUT', '/dev/null'),
			gmail_label='Family/お荷物滞留お知らせメール',
			google=GoogleConfig.from_env(),
			line=LineConfig.from_env(sandbox_mode=sandbox_mode),
			slack=SlackConfig.from_env(),
		)

	def get_status_suffix(self) -> str:
		"""Get suffix for status messages based on mode."""
		return '_sandbox' if self.sandbox_mode else ''

	def get_mode_display(self) -> str:
		"""Get display string for current mode."""
		return '🧪 Running in SANDBOX mode' if self.sandbox_mode else '🚀 Running in PRODUCTION mode'
