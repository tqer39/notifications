#!/usr/bin/env python3
"""OAuth 2.0 setup script for Gmail API."""

import json
import pickle
import base64
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def setup_oauth_credentials(oauth_json_path: str) -> str:
	"""Setup OAuth 2.0 credentials and return encoded token."""
	scopes = ['https://www.googleapis.com/auth/gmail.readonly']

	# Load OAuth client configuration
	with open(oauth_json_path, 'r') as f:
		client_config = json.load(f)

	flow = Flow.from_client_config(client_config, scopes)
	flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # For desktop apps

	# Get authorization URL
	auth_url, _ = flow.authorization_url(prompt='consent')
	print(f'Please visit this URL to authorize the application:')
	print(f'{auth_url}')
	print()

	# Get authorization code from user
	auth_code = input('Enter the authorization code: ')
	flow.fetch_token(code=auth_code)
	creds = flow.credentials

	# Serialize credentials
	token_data = pickle.dumps(creds)
	encoded_token = base64.b64encode(token_data).decode('utf-8')

	print('OAuth setup completed successfully!')
	print("Add this token to your GitHub Secrets as 'GOOGLE_OAUTH_TOKEN':")
	print(f'{encoded_token}')

	# Also save locally for testing
	with open('token.pickle', 'wb') as token:
		pickle.dump(creds, token)

	return encoded_token


if __name__ == '__main__':
	import sys

	if len(sys.argv) != 2:
		print('Usage: python setup_oauth.py <oauth_credentials.json>')
		sys.exit(1)

	oauth_json_path = sys.argv[1]
	setup_oauth_credentials(oauth_json_path)
