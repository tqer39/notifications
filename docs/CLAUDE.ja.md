# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際にClaude Code (claude.ai/code) に対するガイダンスを提供します。

## プロジェクト概要

Gmail to LINE通知システム - Gmail API を使って「fts」ラベルの付いた未読メールを監視し、新しいメールが見つかったらLINE Messaging APIに通知を送信するGitHub Actionsワークフローです。

## 現在の技術スタック

- **言語**: Python 3.13
- **パッケージマネージャー**: uv
- **フレームワーク**: なし（スタンドアロンスクリプト）
- **テスト**: pytest with coverage
- **リンター**: ruff (code style & formatting)
- **型チェック**: mypy
- **CI/CD**: GitHub Actions
- **デプロイ**: GitHub Actions scheduled workflow

## プロジェクト構造

```
notifications/
├── .github/workflows/       # GitHub Actions ワークフロー
│   ├── gmail-to-line-notification.yml  # メイン通知ワークフロー
│   └── test.yml                        # PRテストワークフロー
├── src/                     # ソースコード
│   ├── __init__.py
│   ├── gmail_notifier.py    # Gmail + LINE 通知ロジック
│   └── slack_error_handler.py  # Slack エラー通知
├── tests/                   # テストコード
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_gmail_notifier.py
│   └── test_slack_error_handler.py
├── scripts/                 # 開発用スクリプト
│   ├── test_local.py        # ローカル統合テスト
│   └── run_tests.sh         # テストランナー
├── docs/                    # ドキュメント
│   ├── README.ja.md
│   ├── TESTING.ja.md
│   └── CLAUDE.ja.md
├── Makefile                 # 開発タスク
├── pyproject.toml          # Python プロジェクト設定
├── .env.example            # 環境変数テンプレート
└── README.md               # プロジェクト概要
```

## 開発コマンド

### 基本的なコマンド

```bash
# 初回セットアップ
make setup

# 全テスト実行
make all-tests

# 単体テスト実行
make test

# 静的解析
make lint

# コードフォーマット
make format

# ローカル統合テスト
make local-test

# ヘルプを表示
make help
```

### 直接実行

```bash
# 依存関係インストール
uv sync --frozen --all-extras

# テスト実行
uv run pytest -v --cov=src

# リンター実行
uv run ruff check .
uv run ruff format --check .
uv run mypy .

# ローカルテスト
uv run python scripts/test_local.py
```

## API設定

このプロジェクトは以下のAPIを使用します：

### 必要な GitHub Secrets

| Secret名 | 説明 | 取得方法 |
|----------|------|----------|
| `GOOGLE_CREDENTIALS` | Google Cloud サービスアカウント認証情報 | Google Cloud Console |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API チャンネルトークン | LINE Developers Console |
| `LINE_USER_ID` | 通知送信先のLINEユーザーID | LINE Official Account Manager |
| `SLACK_BOT_TOKEN` | Slack ボットトークン（エラー通知用） | Slack API |
| `SLACK_CHANNEL_ID` | Slack チャンネルID | Slack |

### Gmail API設定

1. Google Cloud Consoleでサービスアカウント作成
2. Gmail API有効化
3. サービスアカウントにGmail読み取り権限付与
4. JSON認証情報をGitHub Secretsに設定

### LINE Messaging API設定

1. LINE Developers Consoleでチャンネル作成
2. Messaging API有効化
3. チャンネルアクセストークン取得
4. ユーザーIDを取得

## コーディング規約

### Python コーディングスタイル

- **インデント**: ハードタブ使用
- **文字列**: シングルクォート使用
- **行長**: 120文字以下
- **型注釈**: 必須（mypyでチェック）

### ファイル構成規約

- すべてのPythonファイルにタイプヒント必須
- docstring必須（Google style）
- テストファイルは対応するソースファイルと同じ構造

### Git コミット規約

- コミットメッセージは英語
- Conventional Commits形式を推奨
- 1コミット1機能

## テスト戦略

### ユニットテスト

- pytest使用
- カバレッジ85%以上
- モックを使用してAPI呼び出しを模擬

### 統合テスト

- `scripts/test_local.py`で完全なワークフローテスト
- 実際のAPIは呼び出さずモックで動作確認

### 静的解析

- ruff: コードスタイル、フォーマット
- mypy: 型チェック（strict設定）

## デプロイメント

### 自動デプロイ

- GitHub Actionsで毎時0分に自動実行
- 手動トリガーも可能

### 環境

- **本番**: GitHub Actions上でワークフロー実行
- **テスト**: ローカル環境でモックテスト

## トラブルシューティング

### よくある問題

1. **Gmail API認証エラー**
   - サービスアカウント権限確認
   - JSON認証情報の形式確認

2. **LINE通知が届かない**
   - チャンネルアクセストークン確認
   - ユーザーID確認

3. **テストが失敗する**
   - `.env.test`ファイル存在確認
   - モックデータ設定確認

### ログ確認

- GitHub Actions: Actionsタブでワークフロー実行ログ確認
- ローカル: `uv run python scripts/test_local.py`でデバッグ

## pre-commitフック

このプロジェクトではpre-commitを使用してコード品質を維持しています。

### セットアップ

```bash
# pre-commitをインストール
pip install pre-commit

# gitフックをインストール
pre-commit install
```

### 手動実行

```bash
# すべてのファイルに対してフックを実行
pre-commit run --all-files

# 特定のフックのみ実行
pre-commit run <hook-id>
```

### 設定されているフック

- **check-added-large-files**: 512KB以上のファイルの追加を防止
- **check-json**: JSONファイルの構文チェック
- **check-yaml**: YAMLファイルの構文チェック
- **detect-aws-credentials**: AWSクレデンシャルの検出
- **detect-private-key**: 秘密鍵の検出（テストファイル除く）
- **end-of-file-fixer**: ファイル末尾の改行を修正
- **mixed-line-ending**: 改行コードをLFに統一
- **trailing-whitespace**: 行末の空白を削除
- **yamllint**: YAMLファイルのリント
- **cspell**: スペルチェック
- **markdownlint-cli2**: Markdownファイルのリント
- **textlint**: 日本語テキストのリント
- **shellcheck**: シェルスクリプトのリント
- **prettier**: YAML/JSONファイルのフォーマット
- **actionlint**: GitHub Actionsワークフローのリント
- **ruff**: Pythonコードのリント・フォーマット
- **mypy**: Python型チェック

## 新機能追加時の手順

1. **ブランチ作成**: `git checkout -b feature/新機能名`
2. **実装**: コーディング規約に従って実装
3. **テスト追加**: ユニットテスト、統合テストを追加
4. **ローカルテスト**: `make all-tests`で全テスト実行
5. **コミット**: 規約に従ってコミット
6. **プルリクエスト**: GitHub でPR作成
7. **CI確認**: GitHub ActionsでCI/CDが成功することを確認

## セキュリティ考慮事項

- 認証情報は絶対にコードにハードコーディングしない
- GitHub Secretsを使用
- テスト時は必ずモックを使用
- 定期的にアクセストークンを更新

## 参考資料

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [LINE Messaging API Documentation](https://developers.line.biz/en/reference/messaging-api/)
- [Slack API Documentation](https://api.slack.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
