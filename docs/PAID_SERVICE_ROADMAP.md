# PayPay AI 有料化ロードマップ

## 現在地

現在は無料ベータ。市場レポートの生成、LINE broadcast、X手動投稿素材、実ETF採点、時系列検証まで実装済み。

無料版のAdSense枠と `ads.txt` 自動生成、有料版の公開プラン比較ページ、詳細分析レポート、
LINE個別push経路まで実装済み。広告は同意対応・プライバシーURL・広告IDが揃うまで無効、
購入導線は法務承認と正式公開フラグが揃うまで無効。

実会員向けHTMLは `premium_report_web.py` が `data/private/premium_report.html` に生成する。
このディレクトリはGit管理対象外であり、GitHub Pagesには公開しない。本番では認証済み会員だけが
アクセスできるWebアプリの保護領域へ `PREMIUM_REPORT_OUTPUT` 相当の保存先を接続する。

会員Webアプリのテスト実装として `member_app.py` と `member_store.py` を追加済み。
ワンタイムメール認証、Stripe subscription Checkout、Webhook署名検証と冪等処理、
Customer Portal、`active/trialing`会員だけのレポート表示を実装している。
SQLiteはローカル試験用のため、本番配備前にPostgreSQL等へ移行し、バックアップと監視を追加する。

有料提供はまだ開始しない。`python commercial_readiness.py` が全項目を通過するまで課金導線を公開しない。

## Phase 0: 法務・商品定義（最優先）

- 日本の金融規制に詳しい弁護士または登録支援の専門家へサービス全体を提示する
- 投資助言・代理業の登録要否を書面で確認する
- 「誰に」「何を」「どの頻度で」「どの対価で」提供するかを固定する
- 利用規約、プライバシーポリシー、特商法表示、返金・解約方針を作成する
- PayPayおよび各社の商標を公式サービスと誤認させない名称・表示にする

完了条件: `LEGAL_REVIEW_APPROVED=true` と公開済み規約URL、問い合わせ窓口。

## Phase 1: 無料クローズドベータ（4〜8週間）

- 50〜100人を上限に、課金せず利用状況を計測する
- 配信成功率、データ欠損率、翌日採点率、解約意向、閲覧率を記録する
- 旧方式の実績を販売訴求に使わない
- モデルは未使用テスト200件以上かつ単純基準+2ptを最低採用条件とする

完了条件: 配信成功率99%以上、重大誤配信0件、採用基準を満たすモデルが1つ以上。

## Phase 2: 会員・配信分離

現在のLINE broadcastは全友だちへ送るため、有料会員限定配信には使えない。

- LINE webhookでユーザーIDを取得し、同意を記録する
- Stripe CustomerとLINE user IDを内部会員IDで紐付ける
- 有効な契約者だけをpush/multicastまたはuser ID audienceへ配信する
- 退会、ブロック、支払い失敗を配信対象へ即時反映する
- 配信ごとに冪等キーを保存して二重送信を防ぐ

会員・課金情報はGitリポジトリやCSVへ保存せず、アクセス制御されたデータベースを使う。

## Phase 3: 課金

- Stripe Checkoutをsubscription modeで利用する
- Webhook署名を検証する
- `checkout.session.completed`、`customer.subscription.updated/deleted`、`invoice.payment_failed`を処理する
- Customer Portalでカード変更、請求履歴、解約を提供する
- 本番鍵をGitHub Secretsまたはホスティング環境のSecretへ保存する

推奨初期商品: 1プランのみ。無料7日間または月額制のどちらか一方から開始し、複雑な段階課金は後回しにする。

## Phase 4: 公開前審査

- 法務承認
- 規約、プライバシー、特商法、サポート導線
- Stripe本番Webhook試験
- LINE会員限定配信試験
- 障害時の配信停止スイッチ
- データ欠損時に推薦を出さないフェイルクローズ
- バックアップ、監視、インシデント対応手順
- 誇大な勝率表示や将来利益の保証表現がないこと

## 推奨アーキテクチャ

- GitHub Actions: 市場分析と公開サマリー生成
- Webアプリ/API: 会員認証、Stripe Checkout、Customer Portal、LINE webhook
- PostgreSQL等: 会員、同意、契約状態、配信履歴
- Secret管理: Stripe・LINE鍵
- 公開ページ: 無料サマリー
- 会員ページ/LINE: 法務確認済みの有料コンテンツ

GitHub Pages相当の静的HTMLだけでは、会員認証と有料コンテンツ保護は実現しない。
