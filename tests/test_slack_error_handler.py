"""Tests for slack_error_handler module."""

import json
import os
from unittest.mock import patch

import responses

from src.slack_error_handler import send_slack_error_notification


class TestSlackErrorHandler:
	"""Tests for slack_error_handler module."""

	@responses.activate
	@patch.dict(
		os.environ,
		{
			'SLACK_BOT_TOKEN': 'test_token',
			'SLACK_CHANNEL_ID': 'test_channel',
			'GITHUB_REPOSITORY': 'owner/repo',
			'GITHUB_RUN_ID': '12345',
		},
	)
	def test_send_slack_error_notification_success(self):
		"""Test successful error notification."""
		responses.add(responses.POST, 'https://slack.com/api/chat.postMessage', json={'ok': True}, status=200)

		send_slack_error_notification()

		assert len(responses.calls) == 1
		request = responses.calls[0].request
		assert request.headers['Authorization'] == 'Bearer test_token'

		body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
		body = json.loads(body_str) if body_str else {}
		assert body['channel'] == 'test_channel'
		assert 'https://github.com/owner/repo/actions/runs/12345' in body['text']
		assert body['mrkdwn'] is True

	@responses.activate
	@patch.dict(
		os.environ,
		{
			'SLACK_BOT_TOKEN': 'test_token',
			'SLACK_CHANNEL_ID': 'test_channel',
			'GITHUB_REPOSITORY': '',
			'GITHUB_RUN_ID': '',
		},
		clear=True,
	)
	def test_send_slack_error_notification_no_github_info(self):
		"""Test error notification without GitHub info."""
		responses.add(responses.POST, 'https://slack.com/api/chat.postMessage', json={'ok': True}, status=200)

		send_slack_error_notification()

		assert len(responses.calls) == 1
		request = responses.calls[0].request
		body_str = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
		body = json.loads(body_str) if body_str else {}
		# Check that the message contains the expected GitHub URL pattern
		expected_url = 'https://github.com//actions/runs/'
		actual_text = body['text']
		assert expected_url in actual_text, f"Expected '{expected_url}' in '{actual_text}'"

	@responses.activate
	@patch.dict(os.environ, {'SLACK_BOT_TOKEN': 'test_token', 'SLACK_CHANNEL_ID': 'test_channel'})
	def test_send_slack_error_notification_api_failure(self, capsys):
		"""Test error notification when Slack API fails."""
		responses.add(
			responses.POST,
			'https://slack.com/api/chat.postMessage',
			json={'ok': False, 'error': 'channel_not_found'},
			status=200,
		)

		send_slack_error_notification()

		captured = capsys.readouterr()
		assert 'Failed to send Slack notification: channel_not_found' in captured.out
