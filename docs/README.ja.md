# notifications

通知サービスを管理するためのリポジトリです。

## 機能

- Gmail to LINE 通知ワークフロー
  - Gmail で "fts" ラベルが付いた未読メールを監視
  - 新しいメールが見つかったら LINE に通知を送信
  - 処理済みのメールを既読にマーク
  - 失敗時は Slack に通知を送信

## セットアップ

### 必要な GitHub Secrets

1. **GOOGLE_OAUTH_TOKEN**
   - Google OAuth 2.0 認証トークン（base64エンコード形式）
   - 必要な権限: Gmail API 読み取りアクセス
   - Google Cloud Console で Gmail API を有効化

2. **LINE_CHANNEL_ACCESS_TOKEN**
   - LINE Messaging API チャンネルアクセストークン
   - LINE Developers Console から作成

3. **LINE_USER_ID**
   - 通知送信先の LINE ユーザー ID
   - LINE Developers Console から取得可能

4. **SLACK_BOT_TOKEN**
   - エラー通知用の Slack ボットトークン
   - 必要なスコープ: `chat:write`

5. **SLACK_CHANNEL_ID**
   - エラー通知を送信する Slack チャンネル ID

### ワークフローの実行

ワークフローは以下のタイミングで実行されます:

- 毎時0分に自動実行 (cron: `0 * * * *`)
- workflow_dispatch による手動実行

### Google OAuth の設定

1. Google Cloud Console で OAuth 2.0 クライアント ID を作成
2. アプリケーションの種類を「デスクトップアプリケーション」に設定
3. 認証情報 JSON をダウンロード
4. `python scripts/setup_oauth.py <oauth_credentials.json>` を実行
5. ブラウザで認証フローを完了
6. 生成された base64 トークンを GitHub Secrets の `GOOGLE_OAUTH_TOKEN` に追加

### LINE の設定

1. LINE Messaging API チャンネルを作成
2. チャンネルアクセストークンを取得
3. LINE ユーザー ID を取得

## 開発

### クイックスタート

```bash
# 初回セットアップ
make setup

# 全テストの実行
make all-tests

# 開発モードでの実行
make dev
```

### ローカルテスト

詳細なテスト手順については、[TESTING.ja.md](TESTING.ja.md) を参照してください。

### プロジェクト構造

```
notifications/
├── .github/workflows/    # GitHub Actions ワークフロー
├── src/                  # ソースコード
│   ├── gmail_notifier.py
│   └── slack_error_handler.py
├── tests/                # テストコード
├── scripts/              # 開発用スクリプト
└── docs/                 # ドキュメント
```

## ライセンス

ISC License
