# Stripeテスト決済の設定手順

この手順では実際の請求は発生しない。Stripe Dashboardは必ずテストモードに切り替え、
`sk_live_`で始まる本番秘密鍵は使用しない。

## 1. ローカル設定ファイルを用意

リポジトリ直下に `.env` を作る。`.env` はGit管理対象外。

```dotenv
SERVICE_STAGE=development
MEMBER_SESSION_SECRET=ここに32文字以上のランダム値
MEMBER_DB_PATH=data/members.db
MEMBER_APP_URL=http://127.0.0.1:8000
MAGIC_LINK_DELIVERY=console

STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID=price_...
STRIPE_WEBHOOK_SECRET=whsec_...
ALLOW_STRIPE_LIVE=false
```

セッション鍵は次のコマンドで生成できる。出力は `.env` にだけ保存する。

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 2. Stripeテスト秘密鍵を取得

1. Stripe Dashboardを開く
2. テストモードへ切り替える
3. 開発者向けのAPIキー画面を開く
4. `sk_test_`で始まるシークレットキーを `.env` の `STRIPE_SECRET_KEY` に設定

秘密鍵をGitHub、チャット、スクリーンショットへ貼らない。

## 3. 月額商品とPriceを作成

まずdry-runで内容を確認する。この時点ではStripeへ何も作成しない。

```bash
python3 stripe_test_setup.py --monthly-yen 980
```

内容確認後、テスト環境へ月額商品を1回だけ作成する。

```bash
python3 stripe_test_setup.py --monthly-yen 980 --confirm-create-test-product
```

出力された `price_id` を `.env` の `STRIPE_PRICE_ID` に設定する。同じコマンドを繰り返すと
商品が重複するため、作成後は再実行しない。

## 4. Stripe CLIでWebhookを転送

Stripe CLIをインストールしてログイン後、別のターミナルで実行する。

```bash
stripe login
stripe listen --forward-to http://127.0.0.1:8000/stripe/webhook
```

表示された `whsec_...` を `.env` の `STRIPE_WEBHOOK_SECRET` に設定する。

## 5. 設定確認と起動

```bash
python3 membership_config_check.py
python3 member_app.py
```

ブラウザで `http://127.0.0.1:8000/login` を開く。開発モードではログインリンクが
起動ターミナルへ表示される。リンクからログインし「テスト決済へ進む」を選ぶ。

Stripeのテストカードを使用し、Checkout完了後にWebhookで契約状態が `active` になることを確認する。
マイページの「支払い・解約を管理」からCustomer Portalへ入り、テスト契約を解約する。

Portal設定が未作成の場合は、次を1回だけ実行する。

```bash
python3 stripe_portal_setup.py
python3 stripe_portal_setup.py --confirm-create-test-portal
```

本番では出力されたConfiguration IDを `STRIPE_PORTAL_CONFIGURATION_ID` に明示設定する。

## 6. 完了確認

- Checkout成功だけでは権限が付かず、Webhook後に有効化される
- `/members/report` は未契約で403、契約中だけ200になる
- 支払い失敗または解約後は有料レポートへ入れない
- 同じWebhookを再送しても二重処理されない

## 本番前に残る作業

- SQLiteからPostgreSQLへ移行
- SMTPまたはトランザクションメールサービスへ接続
- HTTPSの会員アプリをデプロイ
- Stripe Customer Portalの解約設定を確認
- 利用規約、プライバシーポリシー、特商法表示、法務確認
- Stripe本番Webhookを別途登録
