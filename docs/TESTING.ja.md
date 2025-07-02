# ローカルテスト手順

Gmail to LINE通知システムのローカルテスト手順について説明します。

## 🚀 クイックスタート

### 1. 環境設定

```bash
# 1. テスト用環境変数ファイルを作成
cp .env.example .env.test

# 2. .env.testを編集（実際のAPIキーは不要）
# ファイル内のプレースホルダーはテスト用ダミー値のままでOK
```

### 2. 全テスト実行

```bash
# すべてのテストを実行（推奨）
./scripts/run_tests.sh
```

### 3. 個別テスト実行

```bash
# ユニットテストのみ
uv run pytest -v

# 静的解析のみ
uv run ruff check .
uv run mypy .

# ローカル統合テストのみ
uv run python scripts/test_local.py
```

## 📋 詳細なテスト手順

### 事前準備

1. **依存関係のインストール**

   ```bash
   uv sync --frozen --all-extras
   ```

2. **環境変数ファイルの準備**

   ```bash
   # .env.testファイルが存在することを確認
   ls -la .env.test

   # 存在しない場合は作成
   cp .env.example .env.test
   ```

### テストの種類

#### 1. ユニットテスト (pytest)

```bash
# 基本実行
uv run pytest

# 詳細出力 + カバレッジ
uv run pytest -v --cov=src --cov-report=term-missing

# 特定のテストファイル
uv run pytest tests/test_gmail_notifier.py

# 特定のテストケース
uv run pytest tests/test_gmail_notifier.py::TestGmailNotifier::test_init
```

**テスト内容:**

- Gmail API 操作のテスト
- LINE Messaging API 操作のテスト
- Slack API 操作のテスト
- エラーハンドリングのテスト

#### 2. 静的解析

```bash
# コードスタイルチェック
uv run ruff check .

# コードフォーマット確認
uv run ruff format --check .

# 型チェック
uv run mypy .
```

#### 3. ローカル統合テスト

```bash
# モック環境での統合テスト
uv run python scripts/test_local.py
```

**テスト内容:**

- Gmail → LINE → Slack の完全なワークフローテスト
- 環境変数の読み込みテスト
- GitHub Actions出力ファイルのテスト

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. `.env.test` ファイルが見つからない

```bash
❌ .env.testファイルが見つかりません
```

**解決方法:**

```bash
cp .env.example .env.test
```

#### 2. 依存関係のエラー

```bash
❌ ModuleNotFoundError: No module named 'xxx'
```

**解決方法:**

```bash
# 依存関係を再インストール
uv sync --frozen --all-extras
```

#### 3. 型チェックエラー

```bash
❌ mypy エラーが発生
```

**解決方法:**

- pyproject.tomlの`[tool.mypy]`設定を確認
- 必要に応じて型注釈を追加

#### 4. テストが失敗する

```bash
❌ pytest テストが失敗
```

**解決方法:**

1. エラーメッセージを確認
2. モックデータが正しく設定されているか確認
3. 環境変数が正しく読み込まれているか確認

## 📊 テストカバレッジ

現在のテストカバレッジ目標:

- **src/gmail_notifier.py**: 90%以上
- **src/slack_error_handler.py**: 90%以上
- **全体**: 85%以上

カバレッジレポートの確認:

```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 🚢 デプロイ前チェックリスト

ローカルテストが完了したら、以下を確認してからデプロイしてください:

- [ ] 全てのユニットテストがパス
- [ ] 静的解析エラーなし
- [ ] ローカル統合テストが成功
- [ ] カバレッジが目標値以上
- [ ] 実際のAPI認証情報がコードに含まれていない
- [ ] `.env.test` がgitignoreされている

## 🔒 セキュリティ注意事項

### 環境変数の管理

- **✅ 良い例**: `.env.test` にダミー値を設定
- **❌ 悪い例**: 実際のAPIキーを `.env.test` に保存

### 本番環境のテスト

実際のAPIを使用したテストは以下の場合のみ実行:

1. **Gmail API**: 専用のテストアカウントを使用
2. **LINE API**: 開発者向けテストチャンネルを使用
3. **Slack API**: 開発専用ワークスペースを使用

**重要**: 本番アカウントでの直接テストは禁止

## 📈 CI/CDとの連携

GitHub ActionsではPRごとに自動テストが実行されます:

```yaml
# .github/workflows/test.yml で実行される内容
- ruff check/format
- mypy
- pytest (ユニットテストのみ)
```

ローカルテストはGitHub Actionsテストより包括的です。

## 💡 テスト拡張

新機能追加時のテスト追加方法:

1. **ユニットテスト**: `tests/test_*.py` に追加
2. **モックデータ**: `tests/fixtures/mock_data.py` に追加
3. **統合テスト**: `scripts/test_local.py` に追加

詳細は各ファイルのコメントを参照してください。
