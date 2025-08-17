# Gmail to LINE Notification System
# Makefile for common development tasks

.PHONY: help install test lint format type-check clean dev setup setup-oauth all-tests local-test

# デフォルトターゲット
help: ## このヘルプメッセージを表示
	@echo "Gmail to LINE 通知システム - 開発タスク"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# セットアップ
setup: ## 開発環境をセットアップ
	@echo "🔧 開発環境をセットアップ中..."
	uv sync --frozen --all-extras
	@echo "📝 pre-commit フックをインストール中..."
	uv run pre-commit install
	@echo "📋 環境変数ファイルをチェック中..."
	@if [ ! -f .env.test ]; then \
		echo "📄 .env.test を作成中..."; \
		cp .env.example .env.test; \
		echo "✅ .env.test が作成されました"; \
	else \
		echo "✅ .env.test は既に存在します"; \
	fi
	@echo "🎉 セットアップ完了！"

# Google OAuth認証情報発行
setup-oauth: ## Google認証情報(token.pickle)を発行 - 引数: OAUTH_JSON=<path>
	@echo "🌐 Google OAuth認証情報を発行します..."
	@if [ -z "$(OAUTH_JSON)" ]; then \
		echo "❌ エラー: OAUTH_JSON=<oauth_credentials.json> を指定してください"; \
		echo "例: make setup-oauth OAUTH_JSON=credentials.json"; \
		exit 1; \
	fi
	uv run python scripts/setup_oauth.py $(OAUTH_JSON)
	@echo "✅ token.pickle が生成されました（必要に応じて .env へパスを設定してください）"

install: ## 依存関係をインストール
	@echo "📦 依存関係をインストール中..."
	uv sync --frozen --all-extras

# テスト関連
test: ## ユニットテストを実行
	@echo "🧪 ユニットテストを実行中..."
	uv run pytest -v --cov=src --cov-report=term-missing

test-watch: ## ユニットテストを監視モードで実行
	@echo "👀 ユニットテストを監視モードで実行中..."
	uv run pytest-watch

local-test: ## ローカル統合テストを実行
	@echo "🔄 ローカル統合テストを実行中..."
	uv run python scripts/test_local.py

all-tests: ## 全テストスイートを実行
	@echo "🧪 全テストスイートを実行中..."
	./scripts/run_tests.sh

# 静的解析
lint: ## Ruffでコードをリント
	@echo "🔍 Ruffリンターを実行中..."
	uv run ruff check .

lint-fix: ## Ruffでコードをリント（自動修正）
	@echo "🔧 Ruffリンターを実行中（自動修正）..."
	uv run ruff check . --fix

format: ## Ruffでコードをフォーマット
	@echo "🎨 Ruffフォーマッターを実行中..."
	uv run ruff format .

format-check: ## Ruffでフォーマットをチェック
	@echo "📏 Ruffフォーマットをチェック中..."
	uv run ruff format --check .

type-check: ## mypyで型チェック
	@echo "🔎 mypyで型チェック中..."
	uv run mypy .

# 品質チェック
quality: lint format-check type-check ## すべての品質チェックを実行
	@echo "✅ すべての品質チェックが完了しました"

pre-commit: ## pre-commitフックを手動実行
	@echo "🎯 pre-commitフックを実行中..."
	uv run pre-commit run --all-files

# 開発
dev: ## 開発モードでアプリケーションを実行
	@echo "🚀 開発モードで実行中..."
	@echo "📝 .env.testの環境変数を使用します"
	@if [ -f .env.test ]; then \
		export $$(cat .env.test | grep -v '^#' | xargs) && \
		uv run python -m src.gmail_notifier; \
	else \
		echo "❌ .env.testファイルが見つかりません"; \
		echo "💡 'make setup' を実行してください"; \
		exit 1; \
	fi

# GitHub Actions ローカル実行（act使用）
act-test: ## GitHub Actions テストワークフローをローカル実行
	@echo "🎭 GitHub Actions をローカル実行中..."
	@if command -v act >/dev/null 2>&1; then \
		act pull_request; \
	else \
		echo "❌ act がインストールされていません"; \
		echo "💡 インストール: brew install act"; \
	fi

# クリーンアップ
clean: ## 生成ファイルをクリーンアップ
	@echo "🧹 クリーンアップ中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "✅ クリーンアップ完了"

# バージョン情報
version: ## バージョン情報を表示
	@echo "📦 プロジェクト情報"
	@echo "==================="
	@echo "プロジェクト名: gmail-line-notifier"
	@echo "Python バージョン:"
	@uv run python --version
	@echo "uv バージョン:"
	@uv --version
	@echo "依存関係:"
	@uv run pip list | head -10

# CI/CD
ci: quality test ## CI環境でのテスト（品質チェック + ユニットテスト）
	@echo "🏗️ CI環境でのテストが完了しました"

# デバッグ
debug-env: ## 環境変数をデバッグ表示
	@echo "🐛 環境変数デバッグ情報"
	@echo "======================"
	@echo "作業ディレクトリ: $$(pwd)"
	@echo ".env.test 存在確認: $$(if [ -f .env.test ]; then echo '✅ 存在'; else echo '❌ 不存在'; fi)"
	@echo "Python パス: $$(which python3)"
	@echo "uv パス: $$(which uv)"
	@if [ -f .env.test ]; then \
		echo ""; \
		echo "📋 .env.test の内容（機密情報を除く）:"; \
		cat .env.test | grep -v 'TOKEN\|KEY\|SECRET' | head -5; \
	fi

# ドキュメント
docs: ## ドキュメントを表示
	@echo "📚 ドキュメント"
	@echo "============="
	@echo "📖 README.md          : プロジェクト概要"
	@echo "📖 TESTING.md         : テスト手順"
	@echo "📖 CLAUDE.md          : Claude向け情報"
	@echo ""
	@echo "💡 使用方法:"
	@echo "make setup     # 初回セットアップ"
	@echo "make all-tests # 全テスト実行"
	@echo "make dev       # 開発実行"
	@echo "make setup-oauth # Google認証情報(token.pickle)発行"
