# Local Testing Guide

This document explains how to test the Gmail to LINE notification system locally.

[日本語版](docs/TESTING.ja.md)

## 🚀 Quick Start

### 1. Environment Setup

```bash
# 1. Create test environment variable file
cp .env.example .env.test

# 2. Edit .env.test (actual API keys not required)
# Leave placeholder values as dummy data for testing
```

### 2. Run All Tests

```bash
# Run all tests (recommended)
./scripts/run_tests.sh
```

### 3. Individual Test Execution

```bash
# Unit tests only
uv run pytest -v

# Static analysis only
uv run ruff check .
uv run mypy .

# Local integration tests only
uv run python scripts/test_local.py
```

## 📋 Detailed Testing Procedures

### Prerequisites

1. **Install Dependencies**

   ```bash
   uv sync --frozen --all-extras
   ```

2. **Environment Variables Setup**

   ```bash
   # Verify .env.test file exists
   ls -la .env.test

   # Create if not exists
   cp .env.example .env.test
   ```

### Test Types

#### 1. Unit Tests (pytest)

```bash
# Basic execution
uv run pytest

# Verbose output with coverage
uv run pytest -v --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/test_gmail_notifier.py

# Specific test case
uv run pytest tests/test_gmail_notifier.py::TestGmailNotifier::test_init
```

**Test Coverage:**

- Gmail API operations testing
- LINE Messaging API operations testing
- Slack API operations testing
- Error handling testing

#### 2. Static Analysis

```bash
# Code style check
uv run ruff check .

# Code format check
uv run ruff format --check .

# Type checking
uv run mypy .
```

#### 3. Local Integration Tests

```bash
# Integration tests with mock environment
uv run python scripts/test_local.py
```

**Test Coverage:**

- Complete Gmail → LINE → Slack workflow testing
- Environment variable loading testing
- GitHub Actions output file testing

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. `.env.test` File Not Found

```bash
❌ .env.test file not found
```

**Solution:**

```bash
cp .env.example .env.test
```

#### 2. Dependency Errors

```bash
❌ ModuleNotFoundError: No module named 'xxx'
```

**Solution:**

```bash
# Reinstall dependencies
uv sync --frozen --all-extras
```

#### 3. Type Check Errors

```bash
❌ mypy errors occurred
```

**Solution:**

- Check `[tool.mypy]` configuration in pyproject.toml
- Add type annotations as needed

#### 4. Test Failures

```bash
❌ pytest tests failed
```

**Solution:**

1. Check error messages
2. Verify mock data is correctly configured
3. Confirm environment variables are properly loaded

## 📊 Test Coverage

Current test coverage targets:

- **src/gmail_notifier.py**: 90%+
- **src/slack_error_handler.py**: 90%+
- **Overall**: 85%+

View coverage report:

```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 🚢 Pre-Deployment Checklist

After completing local tests, verify the following before deployment:

- [ ] All unit tests pass
- [ ] No static analysis errors
- [ ] Local integration tests succeed
- [ ] Coverage meets target values
- [ ] No actual API credentials in code
- [ ] `.env.test` is gitignored

## 🔒 Security Considerations

### Environment Variable Management

- **✅ Good**: Set dummy values in `.env.test`
- **❌ Bad**: Store actual API keys in `.env.test`

### Production Environment Testing

Only test with actual APIs in these cases:

1. **Gmail API**: Use dedicated test account
2. **LINE API**: Use developer test channel
3. **Slack API**: Use development-only workspace

**Important**: Direct testing with production accounts is prohibited

## 📈 CI/CD Integration

GitHub Actions automatically runs tests for each PR:

```yaml
# Content executed in .github/workflows/test.yml
- ruff check/format
- mypy
- pytest (unit tests only)
```

Local testing is more comprehensive than GitHub Actions testing.

## 💡 Test Extension

How to add tests when adding new features:

1. **Unit Tests**: Add to `tests/test_*.py`
2. **Mock Data**: Add to `tests/fixtures/mock_data.py`
3. **Integration Tests**: Add to `scripts/test_local.py`

See comments in each file for details.

## Testing Framework Details

### pytest Configuration

The project uses pytest with the following configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "-v --strict-markers --strict-config"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests"
]
```

### Mock Testing Strategy

- **Gmail API**: Mocked using `tests/fixtures/mock_data.py`
- **LINE API**: HTTP requests mocked with success/error responses
- **Slack API**: HTTP requests mocked with appropriate responses
- **Environment Variables**: Test-specific values in `.env.test`

### Code Quality Tools

- **ruff**: Fast Python linter and formatter (replacing flake8, black, isort)
- **mypy**: Static type checking with strict configuration
- **pytest**: Test runner with coverage reporting
- **pre-commit**: Automated code quality checks before commits

## Local Development Workflow

1. **Setup**: `make setup` - Install dependencies and create virtual environment
2. **Test**: `make test` - Run unit tests with coverage
3. **Lint**: `make lint` - Run code quality checks
4. **Format**: `make format` - Auto-format code
5. **All Tests**: `make all-tests` - Complete test suite including integration tests

For detailed Makefile commands, run `make help`.
