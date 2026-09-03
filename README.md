
# PayPay AI Market Report

マーケットを定期的に分析し、
PayPayポイント運用の判断を通知するPythonプロジェクト。

## 実装予定

- 市場データ取得
- 売買シグナル
- LINE通知
- GitHub Actions
- AIコメント

## 検証

保存済みのバックテストとML結果を、時系列のテスト期間および多数派基準と比較する。

```bash
python validation.py
python -m unittest discover -s tests -v
```

本番採用には、未使用テストデータ200件以上で多数派基準を2ポイント以上上回ることを最低条件とする。

## 商用化

- ロードマップ: `docs/PAID_SERVICE_ROADMAP.md`
- 有料公開判定: `python commercial_readiness.py`

現在は無料ベータであり、有料公開判定がすべて通過するまで課金を開始しない。

## タイムゾーンと収益化設定

生成日時、履歴日付、採点基準日、ログはすべて日本標準時（Asia/Tokyo）を使う。

有料版の先行案内URLは `PREMIUM_SIGNUP_URL` で設定する。無料版広告はAdSense審査通過後に
`ADS_ENABLED=true`、`ADS_CONSENT_READY=true`、`ADSENSE_CLIENT`、`ADSENSE_SLOT`、
`PRIVACY_URL`を設定した場合だけ表示される。
有料LINE通知にはbroadcastを使わず、契約状態を確認した会員ごとにpush APIを使用する。

`premium.html` は公開用のプラン比較ページであり、有料分析本文は含めない。有料分析や会員情報は
`data/private/` 等へ保存してもGit管理対象にならない。購入導線は `PAID_LAUNCH_ENABLED=true`、
`LEGAL_REVIEW_APPROVED=true`、`STRIPE_CHECKOUT_URL` がすべて揃った場合だけ表示される。

実際の会員レポートHTMLは毎回 `data/private/premium_report.html` に生成される。このファイルは
公開リポジトリへコミットせず、本番では認証付きWebアプリからのみ配信する。

LINEやXへ配信せず、会員レポートだけを生成する場合:

```bash
python3 generate_premium_report.py
```

## 会員認証・Stripeテスト

詳細手順: `docs/STRIPE_TEST_SETUP.md`

公開手順: `docs/DEPLOY_MEMBERS.md`

`member_app.py` はメールのワンタイムリンク認証、Stripe Checkout、署名検証済みWebhook、
Customer Portal、契約中会員だけのレポート表示を提供する。初期段階では必ずStripeテストキーを使う。

```bash
export SERVICE_STAGE=development
export MEMBER_SESSION_SECRET='開発用の十分長いランダム値'
export STRIPE_SECRET_KEY='sk_test_...'
export STRIPE_PRICE_ID='price_...'
export STRIPE_WEBHOOK_SECRET='whsec_...'
export MAGIC_LINK_DELIVERY=console
python3 member_app.py
```

Stripe CLIでローカルWebhookを転送する場合の受信先は
`http://127.0.0.1:8000/stripe/webhook`。ログインは `/login`、マイページは `/account`。
Render無料Webでの検証は `MAGIC_LINK_DELIVERY=resend` と `RESEND_API_KEY`、`EMAIL_FROM` を使用する。
SMTPは無料Webから接続できない。`ALLOW_STRIPE_LIVE=true` は法務・公開判定後のみ設定する。

ローカルは既存のSQLiteを維持する。本番ホスティングでは`DATABASE_URL=postgresql://...`を設定すると
SQLAlchemy経由でPostgreSQLへ切り替わる。会員・契約・認証トークン・Webhook履歴はGitへ保存しない。

テスト商品作成コマンドは既定でdry-runになり、Stripeには何も作成しない。

```bash
python3 stripe_test_setup.py --monthly-yen 980
```

内容を確認後、テスト環境へ実際に作成するときだけ
`--confirm-create-test-product`を付ける。出力された`price_id`を`STRIPE_PRICE_ID`へ設定する。

Customer Portalはdry-run確認後、Sandboxへ1回だけ作成する。

```bash
python3 stripe_portal_setup.py
python3 stripe_portal_setup.py --confirm-create-test-portal
```
