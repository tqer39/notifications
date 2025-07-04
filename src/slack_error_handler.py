"""Slack error notification handler."""

import os

import requests

from .config import SlackConfig


def send_slack_error_notification() -> None:
	"""Send error notification to Slack when workflow fails."""
	try:
		slack_config = SlackConfig.from_env()
	except ValueError as e:
		print(f'Slack configuration error: {e}')
		return

	url = 'https://slack.com/api/chat.postMessage'
	headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {slack_config.bot_token}'}

	# Build error message
	github_repo = os.environ.get('GITHUB_REPOSITORY', '')
	run_id = os.environ.get('GITHUB_RUN_ID', '')
	workflow_url = f'https://github.com/{github_repo}/actions/runs/{run_id}'
	error_message = f'Workflow failed: {workflow_url}\nPlease check the logs for details.'

	data = {
		'channel': slack_config.channel_id,
		'text': f'⚠️ Gmail to LINE Notification Failed\n\n{error_message}',
		'mrkdwn': True,
	}

	response = requests.post(url, headers=headers, json=data)
	response_data = response.json()

	if not response_data.get('ok'):
		print(f'Failed to send Slack notification: {response_data.get("error")}')
	else:
		print('Slack notification sent successfully')


if __name__ == '__main__':
	send_slack_error_notification()
