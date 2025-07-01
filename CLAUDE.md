# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このリポジトリは通知サービスを管理するためのプロジェクトです。現在は初期段階にあり、具体的な実装はまだ行われていません。

## 現在の状態

- **リポジトリステータス**: 初期化済み（`Initial commit`のみ）
- **ブランチ**: `main`
- **実装済みファイル**: README.mdのみ

## 今後の開発における注意事項

### プロジェクトセットアップ時の考慮事項

1. **技術スタックの選定**
   - 通知サービスの要件に応じて適切な言語とフレームワークを選択すること
   - 例: Node.js + Express、Python + FastAPI、Go + Gin等
2. **基本的なディレクトリ構造の提案**

``txt
/notifications
├── src/          # ソースコード
├── tests/        # テストコード
├── docs/         # ドキュメント
├── config/       # 設定ファイル
└── scripts/      # ビルド・デプロイスクリプト

```

3. **通知サービスとして考慮すべき機能**

   - 複数の通知チャネル（Email、SMS、Push通知、Webhook等）のサポート
   - メッセージキューイング
   - 配信スケジューリング
   - 配信状態の追跡
   - テンプレート管理

### 開発開始時の推奨事項

新しい機能を実装する際は、まず以下を確認・設定してください：

1. プロジェクトの基本設定ファイル（package.json、requirements.txt等）を作成
2. リンターとフォーマッター（ESLint、Prettier、Black等）の設定
3. テストフレームワークの導入
4. CI/CDパイプラインの設定
5. 環境変数管理の仕組み

現時点では具体的なビルドコマンドやテストコマンドは存在しないため、プロジェクトの技術スタックが決定次第、このファイルを更新してください。

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
- **detect-private-key**: 秘密鍵の検出
- **end-of-file-fixer**: ファイル末尾の改行を修正
- **mixed-line-ending**: 改行コードをLFに統一
- **trailing-whitespace**: 行末の空白を削除
- **yamllint**: YAMLファイルのリント
- **cspell**: スペルチェック
- **markdownlint-cli2**: Markdownファイルのリント
