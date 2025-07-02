# notifications

A repository for managing notification services.

## Features

- Gmail to LINE notification workflow
  - Monitors Gmail for unread emails with "fts" label
  - Sends notification to LINE when new email is found
  - Marks processed emails as read
  - Sends Slack notification on failure

## Setup

### Required GitHub Secrets

1. **GOOGLE_CREDENTIALS**
   - Google Cloud service account credentials in JSON format
   - Required permissions: Gmail API read access
   - Enable Gmail API in Google Cloud Console

2. **LINE_CHANNEL_ACCESS_TOKEN**
   - LINE Messaging API channel access token
   - Create from LINE Developers Console

3. **LINE_USER_ID**
   - Target LINE user ID to send notifications
   - Can be obtained from LINE Developers Console

4. **SLACK_BOT_TOKEN**
   - Slack bot token for error notifications
   - Required scopes: `chat:write`

5. **SLACK_CHANNEL_ID**
   - Slack channel ID where error notifications will be sent

### Workflow Execution

The workflow runs:

- Automatically every hour (cron: `0 * * * *`)
- Manually via workflow_dispatch

### Google Cloud Setup

1. Create a service account in Google Cloud Console
2. Enable Gmail API
3. Download service account credentials JSON
4. Add the JSON content to GitHub Secrets as `GOOGLE_CREDENTIALS`

### LINE Setup

1. Create a LINE Messaging API channel
2. Get the channel access token
3. Get your LINE user ID
