# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

[日本語版](docs/CLAUDE.ja.md)

## Project Overview

Gmail to LINE Notification System - A GitHub Actions workflow that monitors Gmail for unread emails with the "Family/お荷物滞留お知らせメール" label and sends notifications to LINE Messaging API when new emails are found.

## Current Technology Stack

- **Language**: Python 3.13
- **Package Manager**: uv
- **Framework**: None (standalone scripts)
- **Testing**: pytest with coverage
- **Linter**: ruff (code style & formatting)
- **Type Checking**: mypy
- **CI/CD**: GitHub Actions
- **Deployment**: GitHub Actions scheduled workflow

## Project Structure

```
notifications/
├── .github/workflows/       # GitHub Actions workflows
│   ├── gmail-to-line-notification.yml  # Main notification workflow
│   └── test.yml                        # PR testing workflow
├── src/                     # Source code
│   ├── __init__.py
│   ├── gmail_notifier.py    # Gmail + LINE notification logic
│   └── slack_error_handler.py  # Slack error notifications
├── tests/                   # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_gmail_notifier.py
│   └── test_slack_error_handler.py
├── scripts/                 # Development scripts
│   ├── test_local.py        # Local integration testing
│   └── run_tests.sh         # Test runner
├── docs/                    # Documentation
│   ├── README.ja.md
│   ├── TESTING.ja.md
│   └── CLAUDE.ja.md
├── Makefile                 # Development tasks
├── pyproject.toml          # Python project configuration
├── .env.example            # Environment variables template
└── README.md               # Project overview
```

## Development Commands

### Essential Commands

```bash
# Initial setup
make setup

# Run all tests
make all-tests

# Run unit tests
make test

# Run static analysis
make lint

# Format code
make format

# Run local integration tests
make local-test

# Show help
make help
```

### Direct Execution

```bash
# Install dependencies
uv sync --frozen --all-extras

# Run tests
uv run pytest -v --cov=src

# Run linting
uv run ruff check .
uv run ruff format --check .
uv run mypy .

# Local testing
uv run python scripts/test_local.py
```

## API Configuration

This project uses the following APIs:

### Required GitHub Secrets

| Secret Name | Description | How to Obtain |
|-------------|-------------|---------------|
| `GOOGLE_OAUTH_TOKEN` | OAuth 2.0 credentials with refresh token (base64 encoded pickle) | Generated via local OAuth flow |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API channel token | LINE Developers Console |
| `LINE_CHANNEL_ACCESS_TOKEN_SANDBOX` | LINE Messaging API sandbox channel token | LINE Developers Console |
| `LINE_USER_ID` | LINE user ID for notifications | LINE Official Account Manager |
| `LINE_USER_ID_SANDBOX` | LINE user ID for sandbox notifications | LINE Official Account Manager |
| `SLACK_BOT_TOKEN` | Slack bot token (for error notifications) | Slack API |
| `SLACK_CHANNEL_ID` | Slack channel ID | Slack |

### Gmail API Setup

**OAuth 2.0 Authentication (Current Implementation):**

1. Create OAuth 2.0 client credentials in Google Cloud Console
2. Enable Gmail API
3. Generate OAuth token locally using `scripts/test_local.py`
4. Base64 encode the generated `token.pickle` file
5. Set encoded token as `GOOGLE_OAUTH_TOKEN` in GitHub Secrets

**Important Notes:**

- The OAuth token includes a refresh_token for automatic renewal when expired
- Token generation requires `access_type='offline'` to obtain refresh_token
- GitHub Actions automatically refreshes expired tokens using the refresh_token

### LINE Messaging API Setup

1. Create channel in LINE Developers Console
2. Enable Messaging API
3. Obtain channel access token
4. Get user ID

## Coding Standards

### Python Coding Style

- **Indentation**: Hard tabs
- **Strings**: Single quotes
- **Line Length**: 120 characters max
- **Type Annotations**: Required (checked by mypy)

### File Organization Standards

- All Python files must have type hints
- Docstrings required (Google style)
- Test files mirror source file structure

### Git Commit Standards

- Commit messages in English
- Conventional Commits format recommended
- One feature per commit

## Testing Strategy

### Unit Tests

- Uses pytest
- 85%+ coverage required
- Mock API calls for testing

### Integration Tests

- `scripts/test_local.py` for complete workflow testing
- No actual API calls, only mocked operations

### Static Analysis

- ruff: Code style and formatting
- mypy: Type checking (strict configuration)

## Deployment

### Automated Deployment

- GitHub Actions runs automatically 3 times daily at 7:00, 12:00, and 17:00 JST
- Manual triggering also available

### Environments

- **Production**: Workflow execution on GitHub Actions
- **Testing**: Local environment with mocked tests

## Troubleshooting

### Common Issues

1. **Gmail API Authentication Error**
   - Check if `GOOGLE_OAUTH_TOKEN` has expired and lacks refresh_token
   - Regenerate OAuth token with `access_type='offline'` if refresh fails
   - Verify OAuth client credentials configuration

2. **LINE Notifications Not Received**
   - Verify channel access token
   - Confirm user ID

3. **Test Failures**
   - Check `.env.test` file exists
   - Verify mock data configuration

### Log Checking

- GitHub Actions: Check workflow execution logs in Actions tab
- Local: Run `uv run python scripts/test_local.py` for debugging

## Pre-commit Hooks

This project uses pre-commit to maintain code quality.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install
```

### Manual Execution

```bash
# Run hooks on all files
pre-commit run --all-files

# Run specific hook only
pre-commit run <hook-id>
```

### Configured Hooks

- **check-added-large-files**: Prevent files larger than 512KB
- **check-json**: JSON syntax validation
- **check-yaml**: YAML syntax validation
- **detect-aws-credentials**: AWS credential detection
- **detect-private-key**: Private key detection (excludes test files)
- **end-of-file-fixer**: Fix file endings
- **mixed-line-ending**: Standardize line endings to LF
- **trailing-whitespace**: Remove trailing whitespace
- **yamllint**: YAML file linting
- **cspell**: Spell checking
- **markdownlint-cli2**: Markdown file linting
- **textlint**: Japanese text linting
- **shellcheck**: Shell script linting
- **prettier**: YAML/JSON file formatting
- **actionlint**: GitHub Actions workflow linting
- **ruff**: Python code linting and formatting
- **mypy**: Python type checking

## Adding New Features

1. **Create Branch**: `git checkout -b feature/feature-name`
2. **Implementation**: Follow coding standards
3. **Add Tests**: Add unit and integration tests
4. **Local Testing**: Run `make all-tests`
5. **Commit**: Follow commit standards
6. **Pull Request**: Create PR on GitHub
7. **CI Verification**: Ensure GitHub Actions CI/CD passes

## Security Considerations

- Never hardcode credentials in code
- Use GitHub Secrets
- Always use mocks for testing
- Regularly rotate access tokens

## Architecture Notes

### Configuration System

The application uses a centralized configuration system (`src/config.py`) that:

- Loads environment variables automatically
- Supports sandbox mode for testing with separate LINE channels
- Provides type-safe configuration classes for Google, LINE, and Slack APIs
- Handles both production and sandbox environments through environment variable selection

### Gmail Integration

- Uses OAuth 2.0 authentication with automatic token refresh
- Searches for emails with "Family/お荷物滞留お知らせメール" label
- Processes only unread emails
- Marks emails as read after processing
- Handles token expiration gracefully with refresh_token mechanism

### LINE Integration

- Sends formatted notifications
- Includes email subject, sender, and body
- Error handling for failed deliveries

### Slack Integration

- Error notifications only
- Includes workflow details and error messages
- Links to GitHub Actions for troubleshooting

### Error Handling

- Comprehensive try-catch blocks
- Detailed error logging
- Slack notifications for failures
- GitHub Actions output for debugging

## Mock Testing Strategy

### Gmail API Mocking

- Uses `tests/fixtures/mock_data.py`
- Simulates various email formats (plain text, multipart)
- Tests error conditions

### LINE API Mocking

- Mocks HTTP requests and responses
- Tests both success and error scenarios
- Validates message formatting

### Slack API Mocking

- Mocks error notification sending
- Tests proper error message formatting
- Validates channel and token usage

## Development Workflow

1. **Setup**: Clone repo and run `make setup`
2. **Development**: Make changes following coding standards
3. **Testing**: Run `make all-tests` frequently
4. **Pre-commit**: Hooks run automatically on commit
5. **PR**: Create pull request for review
6. **CI/CD**: GitHub Actions runs tests automatically
7. **Merge**: Merge after CI passes and review approval

## Reference Documentation

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [LINE Messaging API Documentation](https://developers.line.biz/en/reference/messaging-api/)
- [Slack API Documentation](https://api.slack.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)

## Performance Considerations

- Efficient Gmail API queries with labels
- Batch processing for multiple emails
- Minimal API calls to reduce rate limiting
- Error retry mechanisms with exponential backoff

## Monitoring and Alerts

- GitHub Actions workflow status
- Slack error notifications
- Email processing logs
- API rate limit monitoring

## Development Diary

When making significant changes to the codebase, maintain a development diary in `docs/dev-diary/YYYY-MM-DD.md` format.

### Purpose

- Record major changes and their rationale
- Document technical decisions and implementation details
- Track issues encountered and their solutions
- Provide context for future developers

### Creation Rules

Development diaries should be created following these rules:

1. **When to Create**: Create a new diary entry when there are uncommitted changes or undocumented work from previous commits
2. **File Naming**: Use the format `docs/dev-diary/YYYY-MM-DD.md` with today's date
3. **Automatic Creation**: If a file for today's date doesn't exist, create it automatically
4. **Coverage Period**: Document all development work since the last diary entry, regardless of when it was committed
5. **Timing**: Create the diary entry at the end of a development session or when requested

### Format

Each diary entry should include:

- **Overview**: Brief summary of the work
- **Implementation Details**: Technical changes made
- **Test Results**: Verification of changes
- **Issues and Solutions**: Problems encountered and how they were resolved
- **Future Considerations**: Next steps or improvements needed
- **Mood**: Developer's feelings, learnings, and reflections during the work
- **Refactoring Opportunities**: Areas of code that could be improved or restructured

### Example

See `docs/dev-diary/2025-07-03.md` for the OAuth 2.0 authentication migration example.
