# DCR English Lab ディレクトリ調査レポート

調査日時: 2026-11-24

## 1. 概要

このディレクトリは、株式会社第一コンピュータリソース新卒採用向けの一般教養英語を想定した、ブラウザで動作する独自学習アプリです。

公式過去問ではなく独自作成問題を使用します。`index.html` 単体で動作し、問題データ、画面、JavaScript、学習状態の保存が設計されています。

## 2. ファイル構成

| ファイル | 役割 |
|---|---|
| `README.md` | プロジェクト概要、利用方法、問題構成、操作仕様、更新手順 |
| `index.html` | 問題データ埋込み済みのスタンドアロン版アプリ |
| `app_template.html` | 問題埋込み用プレースホルダー `__DATA__` を持つHTMLテンプレート |
| `build_bank.py` | 問題バンク生成、重複・形式検証、`questions.json` 出力 |
| `rebuild_html.py` | `questions.json` をテンプレートへ埋め込み、`index.html` を再生成 |
| `questions.json` | カテゴリ定義と全問題データ |
| `.gitignore` | `.env` を除外するローカル設定 |
| `.env` | 環境変数を格納する設定ファイル |

## 3. 問題データ

調査時点で確認できた内容は次の通りです。

- カテゴリ数: 16
- 問題数: 365
- レベル1: 197問
- レベル2: 131問
- レベル3: 37問

分野別問題数:

| 分野 | 問題数 |
|---|---:|
| agreement | 17 |
| tense | 24 |
| perfect | 18 |
| modal | 14 |
| passive | 14 |
| gerund | 18 |
| comparison | 14 |
| relative | 14 |
| preposition | 24 |
| conjunction | 16 |
| article | 14 |
| wordform | 18 |
| conditional | 14 |
| vocab_general | 51 |
| vocab_business | 50 |
| reading | 45 |

文法カテゴリは13分野、語彙カテゴリは2分野、読解は1分野です。

## 4. データ生成フロー

1. `build_bank.py` を実行する。
2. 問題の選択肢をシャッフルし、IDと解答インデックスを生成する。
3. 問題形式、選択肢数、重複、解答範囲を検証する。
4. カテゴリ定義と問題を `questions.json` に書き出す。
5. `rebuild_html.py` を実行する。
6. `questions.json` を読み込み、テンプレートの `__DATA__` をJSON文字列へ埋め込む。
7. `index.html` を再生成する。

`build_bank.py` はランダムシード `2207` を設定しているため、選択肢の並びは再現可能です。

## 5. アプリ仕様

READMEに記載された主な機能:

- 5分スプリントと分野別演習
- 弱点抽出とミス補強
- 不正解10分後、正解1日後から始まる簡易間隔反復
- 20/30/40問、複数の制限時間から選べる模試
- 累計正答率、分野別成績、直近7日間の回答量、演習履歴
- 数字キー1〜4、Enterキー、スマートフォン操作
- ブラウザの `localStorage` に学習データを保存
- JSONによる学習データのバックアップ、復元

## 6. UI構成

テンプレートは、デスクトップでは左サイドナビ、モバイルでは下部ナビを持つレスポンシブ構成です。

主な画面は次のとおりです。

- ホーム
- インプット
- 分野別演習
- 復習
- 模試
- 分析
- 設定

演習中はモバイル下部ナビを非表示にし、問題への集中を優先します。

## 7. Git状態

調査時点のブランチは `main`、最新コミットは `29ef771 1st` です。

Gitで管理されている主なファイル:

- `README.md`
- `app_template.html`
- `build_bank.py`
- `index.html`
- `questions.json`
- `rebuild_html.py`

未追跡ファイルとして `.gitignore` が確認されました。`.env` は `.gitignore` により除外されていますが、`.gitignore` 自体はまだコミットされていない状態です。

## 8. セキュリティ上の注意

`.env` にAPIキーと思われる値が含まれていました。キー自体はレポートには記載しません。

- `.env` はGitで管理されていませんが、`.gitignore` は未コミットです。
- Git履歴や共有ディレクトリに以前配置した形跡がないか確認する必要があります。
- キーは失効・再発行し、公開リポジトリへアップロードしないでください。
- キーをソースコードへ埋め込まない運用を推奨します。

## 9. 確認済み事項

- `questions.json` は365問を保持している。
- カテゴリ定義は16種類ある。
- レベル分布はレベル1が197、レベル2が131、レベル3が37。
- リポジトリは `main` ブランチで、主要生成物とスクリプトが追跡済み。
- `.env` はローカルの `.gitignore` により除外されている。

## 10. 推奨事項

1. 生成フローをスクリプト化し、問題生成後にJSON検証とHTML再生成を連続実行できるようにする。

## 11. AIチューター統合レポート

### 実装状況

- 誤答結果カードに「間違えた理由」「やさしく説明」「類題を解く」の3操作を追加した。
- 結果画面の既存解説、採点、復習間隔、模試制限時間、履歴保存には変更を加えていない。
- `POST /api/tutor` を同一Origin向けに実装した。
- サーバー側で問題ID、選択番号、actionを検証し、正解・問題文はサーバーの問題バンクから取得する。
- モック時と本番時で応答モードを分け、本番設定不足時はフェイルクローズする。
- 生成文章は `textContent` を使用し、類題の回答は学習成績へ記録しない。

### 主な変更ファイル

- `app_template.html` / `index.html` — 結果画面へのAI操作UI
- `assets/tutor-ui.css` / `assets/tutor-ui.js` — UIと通信処理
- `functions/api/tutor.js` — API検証、レート制限、OpenAI呼び出し
- `functions/_lib/` — 問題バンク、モック、プロンプト、JSON Schema
- `scripts/build_site.js` — ルート版とPages出力の生成
- `scripts/check_bank.js` — 問題バンク検証
- `tests/api.test.js` — API入力検証・モック・スキーマテスト
- `package.json` / `wrangler.toml` — ビルド・テスト・Pages設定

### 実行コマンド

- `npm run check:bank`
- `npm run build`
- `npm test`

### ローカル検証結果

- 問題バンク: 365問、16カテゴリ、重複・選択肢・解答範囲を検証済み
- ビルド: ルート版 `index.html` と `site/index.html` を生成済み
- APIテスト: 8件すべて成功
- HTTP確認: `/`、`/assets/tutor-ui.js`、`/site/index.html` がローカルで200応答
- レスポンシブ検証は静的確認まで実施。320/390/768/1280pxの実ブラウザ操作は未検証

### Cloudflare設定

- `wrangler.toml` の出力先は `./site` のPages構成を示す。
- Git連携、Pages Functionsと独立Workersのどちらが実運用かは設定・ダッシュボード情報から確定できていない。
- `wrangler.toml` にレートリミッターの初期設定はあるが、Pagesプロジェクトへの適用可否は未確認。
- 本番で必要なSecret: `OPENAI_API_KEY`
- 環境変数候補: `OPENAI_MODEL=gpt-6-luna`、`APP_ENV=production`
- 現在のローカル `.env` は変数名 `OPEN_AI_KEY` を使用しているため、統合APIが読む `OPENAI_API_KEY` Secretとは別名として扱われる。値の移行時は必ずCloudflare Secretへ保存し、秘密文字列をファイルへ残さない。

### セキュリティ確認

- Git履歴に `.env` または `.dev.vars` の追加履歴は見つからなかった。
- `.env` の値はレポート・ログ・成果物へ記載していない。
- `.gitignore` は `.env`、`.dev.vars`、`.wrangler`、AI成果物を除外する。
- レートリミッター未設定時は503で停止し、設定不足をfail closedとする。
- 本番公開前にAPIキー失効・再発行、WAF/Access、OpenAI支出上限の確認が必要。

### 未検証事項

- 実OpenAI Responses APIへの接続
- `gpt-6-luna` が該当OpenAIアカウントで利用可能か
- 実Cloudflare Pages/Workersへのデプロイ
- 実レート制限の動作
- 320/390/768/1280pxでの実ブラウザ操作
- 16分野×3 actionの品質監査

実APIへの接続・デプロイは明示的な指示がないため未実施である。

### ロールバック

AI関連ファイルを削除または無効化し、`app_template.html` と `index.html` を統合前の結果カードに戻す。`npm run build` の再実行でルート版とPages出力を再生成し、採点・復習・模試ロジックは変更しない。

### 想定API費用

入力1,000トークン・出力350トークンの場合の参考値は約 `$0.000275 / 回` である。実利用はモデル、推論トークン、キャッシュ、為替レートに左右されるため、CloudflareとOpenAIの利用ダッシュボードで実測が必要。
