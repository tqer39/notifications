#!/bin/bash
set -e

echo "🧪 通知システム テストスイート"
echo "================================"

# プロジェクトルートに移動
cd "$(dirname "$0")/.."

# 環境変数ファイルの確認
if [ ! -f ".env.test" ]; then
	echo "❌ .env.test ファイルが見つかりません"
	echo "📝 .env.example を参考に .env.test を作成してください"
	exit 1
fi

echo "✅ 環境変数ファイル確認完了"

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
uv sync --frozen --all-extras

# 静的解析
echo "🔍 静的解析実行中..."
echo "  - Ruff (リンター)"
uv run ruff check .

echo "  - Ruff (フォーマッター)"
uv run ruff format --check .

echo "  - mypy (型チェック)"
uv run mypy .

# ユニットテスト
echo "🧪 ユニットテスト実行中..."
uv run pytest -v --cov=src --cov-report=term-missing

# ローカル統合テスト
echo "🔄 ローカル統合テスト実行中..."
uv run python scripts/test_local.py

echo ""
echo "🎉 すべてのテストが完了しました！"
echo "✅ コードは本番環境にデプロイ可能です"
