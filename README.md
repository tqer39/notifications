# Gmail to LINE Notification System

A GitHub Actions workflow that monitors Gmail for specific labeled emails and sends notifications to LINE Messaging API.

[日本語版](docs/README.ja.md)

## Features

- **Gmail Monitoring**: Automatically checks for unread emails with "fts" label
- **LINE Notifications**: Sends email content to LINE when new messages are found
- **Email Management**: Marks processed emails as read to avoid duplicate notifications
- **Error Handling**: Sends Slack notifications on workflow failures
- **Flexible Execution**: Runs hourly or can be triggered manually

## Quick Start

### Prerequisites

- Google account with Gmail API enabled
- LINE Developers account with Messaging API channel
- Slack workspace with bot token (for error notifications)
- GitHub repository with Actions enabled

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/notifications.git
   cd notifications
   ```

2. **Configure GitHub Secrets**

   Add the following secrets to your GitHub repository:

   | Secret Name | Description |
   |------------|-------------|
   | `GOOGLE_OAUTH_TOKEN` | Google OAuth 2.0 credentials token (base64 encoded) |
   | `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API channel token |
   | `LINE_USER_ID` | Target LINE user ID |
   | `SLACK_BOT_TOKEN` | Slack bot token (xoxb-...) |
   | `SLACK_CHANNEL_ID` | Slack channel ID (C...) |

3. **Deploy**

   The workflow will automatically run every hour once deployed.

## Configuration

### Google OAuth Setup

1. **Create OAuth 2.0 Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Choose "Desktop application" type
   - Download the JSON credentials file

2. **Enable Gmail API**
   - Go to APIs & Services > Library
   - Search for "Gmail API"
   - Enable the API

3. **Generate OAuth Token**
   - Run the setup script: `python scripts/setup_oauth.py <oauth_credentials.json>`
   - Follow the authorization flow in your browser
   - Copy the generated base64 token to GitHub Secrets as `GOOGLE_OAUTH_TOKEN`

### LINE Messaging API Setup

1. **Create a Channel**
   - Go to [LINE Developers Console](https://developers.line.biz)
   - Create a new provider or use existing one
   - Create a Messaging API channel

2. **Get Credentials**
   - Channel access token: Found in the Messaging API tab
   - User ID: Use LINE Official Account Manager or API to get your user ID

### Slack Setup (Optional)

1. **Create a Slack App**
   - Go to [Slack API](https://api.slack.com/apps)
   - Create a new app for your workspace

2. **Configure Bot Token**
   - Add OAuth scope: `chat:write`
   - Install app to workspace
   - Copy the bot token (xoxb-...)

3. **Get Channel ID**
   - Right-click on the target channel
   - View channel details
   - Copy the channel ID

## Development

### Local Setup

```bash
# Install development environment
make setup

# Run all tests
make all-tests

# Run in development mode
make dev
```

### Project Structure

```
notifications/
├── .github/workflows/       # GitHub Actions workflows
│   ├── gmail-to-line-notification.yml
│   └── test.yml
├── src/                     # Source code
│   ├── __init__.py
│   ├── gmail_notifier.py    # Gmail and LINE notification logic
│   └── slack_error_handler.py
├── tests/                   # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_gmail_notifier.py
│   └── test_slack_error_handler.py
├── scripts/                 # Development scripts
│   ├── test_local.py
│   └── run_tests.sh
├── docs/                    # Documentation
├── Makefile                 # Development tasks
├── pyproject.toml          # Python project configuration
└── README.md               # This file
```

### Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Test individual components with pytest
- **Integration Tests**: Test the complete workflow with mocks
- **Static Analysis**: Code quality checks with ruff and mypy

For detailed testing instructions, see [TESTING.md](TESTING.md).

## Workflow Details

### Execution Schedule

- **Automatic**: Runs every hour at minute 0 (cron: `0 * * * *`)
- **Manual**: Can be triggered via GitHub Actions UI

### Email Processing Flow

1. Connect to Gmail API using OAuth 2.0 credentials
2. Search for unread emails with "fts" label
3. Retrieve the first unread email (if any)
4. Extract email content (subject, sender, body)
5. Send notification to LINE
6. Mark email as read
7. Report status to GitHub Actions

### Error Handling

If any step fails:

1. The workflow reports failure
2. Slack notification is sent with error details
3. Email remains unread for next execution

## Monitoring

### GitHub Actions

- View workflow runs in the Actions tab
- Check logs for detailed execution information
- Monitor success/failure rates

### Notifications

- **Success**: LINE message with email content
- **Failure**: Slack message with error details and workflow link

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Gmail API authentication fails | Check OAuth 2.0 token validity and Gmail API enablement |
| LINE notification not received | Verify channel access token and user ID |
| Slack error notification fails | Confirm bot token has `chat:write` scope |
| No emails found | Ensure emails have "fts" label and are unread |

### Debug Steps

1. Check GitHub Actions logs
2. Verify all secrets are correctly set
3. Test with `make local-test` for local debugging
4. Review error messages in Slack notifications
5. Regenerate OAuth token if authentication fails

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests with `make all-tests`
5. Submit a pull request

## Security

- Never commit credentials to the repository
- Use GitHub Secrets for all sensitive data
- Regularly rotate access tokens
- Review OAuth application permissions
- Keep OAuth credentials JSON file secure

## License

ISC License - see [LICENSE](LICENSE) file for details

## Support

- Create an issue for bug reports or feature requests
- Check [existing issues](https://github.com/your-username/notifications/issues) before creating new ones
- See [CLAUDE.md](CLAUDE.md) for AI assistant guidance
