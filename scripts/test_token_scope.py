#!/usr/bin/env python3
"""Test OAuth token scope."""

import base64
import pickle
import sys
from google.oauth2.credentials import Credentials


def test_token_scope(token_string: str) -> None:
	"""Test the scope of an OAuth token."""
	try:
		# Remove any whitespace or newlines
		token_string = token_string.strip()

		# Decode token
		token_data = base64.b64decode(token_string.encode('utf-8'))
		creds = pickle.loads(token_data)

		print(f'Token is valid: {creds.valid}')
		print(f'Token expiry: {creds.expiry}')
		print(f'Token scopes: {creds.scopes}')

		# Check if token has gmail.modify scope
		if creds.scopes and 'https://www.googleapis.com/auth/gmail.modify' in creds.scopes:
			print('✅ Token has gmail.modify scope - can mark emails as read')
		elif creds.scopes and 'https://www.googleapis.com/auth/gmail.readonly' in creds.scopes:
			print('❌ Token only has gmail.readonly scope - cannot mark emails as read')
		else:
			print(f'⚠️  Unknown scopes: {creds.scopes}')

	except Exception as e:
		print(f'Error testing token: {e}')


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Usage: python test_token_scope.py <base64_token>')
		print('Or use environment variable: GOOGLE_OAUTH_TOKEN=<token> python test_token_scope.py')

		# Try to get from environment
		import os
		token = os.environ.get('GOOGLE_OAUTH_TOKEN')
		if token:
			print('\nTesting token from environment variable...')
			test_token_scope(token)
		else:
			sys.exit(1)
	else:
		test_token_scope(sys.argv[1])
