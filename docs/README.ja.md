# notifications

通知サービスを管理するためのリポジトリです。

## 機能

- Gmail to LINE 通知ワークフロー
  - Gmail で "Family/お荷物滞留お知らせメール" ラベルが付いた未読メールを監視
  - 新しいメールが見つかったら LINE に通知を送信
  - 処理済みのメールを既読にマーク
  - 失敗時は Slack に通知を送信

## セットアップ

### 必要な GitHub Secrets

1. **GOOGLE_OAUTH_TOKEN**
   - Google OAuth 2.0 認証トークン（base64エンコード形式）
   - 必要な権限: Gmail API の読み取りと変更アクセス（gmail.modify スコープ）
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

- 日本時間 7:00, 12:00, 17:00 に自動実行（1日3回）
- workflow_dispatch による手動実行

### Google OAuth の設定

1. **OAuth 2.0 クライアント ID を作成**
   - [Google Cloud Console](https://console.cloud.google.com) にアクセス
   - APIs & Services > Credentials に移動
   - 「認証情報を作成」> 「OAuth 2.0 クライアント ID」を選択
   - アプリケーションの種類を「デスクトップアプリケーション」に設定
   - 認証情報 JSON をダウンロード

2. **Gmail API を有効化**
   - APIs & Services > Library に移動
   - 「Gmail API」を検索
   - API を有効化

3. **OAuth トークンを生成**

   ```bash
   # 依存関係をインストール
   uv sync --frozen

   # セットアップスクリプトを実行
   uv run python scripts/setup_oauth.py <ダウンロードした認証情報JSONのパス>
   ```

   - ブラウザで認証フローに従う
   - Gmail のメッセージの読み取りと変更権限を許可
   - 表示された認証コードを入力

4. **トークンの権限を確認**

   ```bash
   # トークンが正しい権限を持っているか確認
   uv run python scripts/check_local_token.py
   ```

   以下のメッセージが表示されれば成功:

   ```
   ✅ Token has gmail.modify scope - can mark emails as read
   ```

5. **GitHub Secrets に追加**

   セットアップスクリプトが出力した base64 エンコードされたトークンをコピーして:
   - GitHub リポジトリの Settings > Secrets and variables > Actions に移動
   - 「New repository secret」をクリック
   - Name: `GOOGLE_OAUTH_TOKEN`
   - Value: コピーしたトークンを貼り付け

   **注意**: このトークンはメールの読み取りと既読設定の権限を持ちます。ワークフローが正常に動作するために必要です。

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
│   ├── setup_oauth.py    # OAuth トークン生成
│   ├── check_local_token.py # トークン権限確認
│   └── test_local.py     # ローカルテスト
└── docs/                 # ドキュメント
```

## トラブルシューティング

### よくある問題

| 問題 | 解決方法 |
|------|----------|
| Gmail API 認証エラー | `uv run python scripts/setup_oauth.py` でトークンを再生成 |
| "Request had insufficient authentication scopes" エラー | トークンが readonly スコープです。modify スコープで再生成が必要 |
| LINE 通知が届かない | チャンネルアクセストークンとユーザー ID を確認 |
| Slack エラー通知が失敗 | ボットトークンが `chat:write` スコープを持っているか確認 |
| メールが見つからない | メールに "Family/お荷物滞留お知らせメール" ラベルがあり、未読であることを確認 |

## ライセンス

ISC License
