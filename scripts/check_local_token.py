#!/usr/bin/env python3
"""Check local token.pickle file scope."""

import os
import pickle


def check_local_token() -> None:
	"""Check the scope of local token.pickle file."""
	token_file = 'token.pickle'

	if not os.path.exists(token_file):
		print(f'Token file {token_file} not found')
		return

	try:
		with open(token_file, 'rb') as f:
			creds = pickle.load(f)

		print(f'Token is valid: {creds.valid}')
		print(f'Token expiry: {creds.expiry}')
		print(f'Token scopes: {creds.scopes}')

		# Check if token has gmail.modify scope
		if creds.scopes and 'https://www.googleapis.com/auth/gmail.modify' in creds.scopes:
			print('✅ Token has gmail.modify scope - can mark emails as read')
		elif creds.scopes and 'https://www.googleapis.com/auth/gmail.readonly' in creds.scopes:
			print('❌ Token only has gmail.readonly scope - cannot mark emails as read')
			print('\nYou need to regenerate the token with gmail.modify scope:')
			print('1. Run: uv run python scripts/setup_oauth.py <oauth_credentials.json>')
			print('2. Update GOOGLE_OAUTH_TOKEN in GitHub Secrets with the new token')
		else:
			print(f'⚠️  Unknown scopes: {creds.scopes}')

	except Exception as e:
		print(f'Error reading token file: {e}')


if __name__ == '__main__':
	check_local_token()
