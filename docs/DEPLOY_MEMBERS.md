# 会員アプリ公開手順

`render.yaml`は、次の3要素を同時に作るBlueprint定義。

- HTTPS会員Webアプリ
- PostgreSQL会員DB
- 平日9:20 JSTに有料レポートを生成するCron Job（UTC 0:20）

## 公開前の安全条件

最初はStripe Sandboxキーだけを設定し、`ALLOW_STRIPE_LIVE=false`を維持する。
公開URLでCheckout、Webhook、Portal、解約を一巡するまで本番キーへ変更しない。

## デプロイ

1. ホスティングサービスでこのGitHubリポジトリを接続
2. `render.yaml`をBlueprintとして読み込む
3. Webサービスの未同期環境変数を設定
4. デプロイ後に `https://公開URL/healthz` を確認
5. Stripe Sandboxに `https://公開URL/stripe/webhook` をWebhookとして登録
6. Stripeの新しい署名シークレットを `STRIPE_WEBHOOK_SECRET` に設定
7. `MEMBER_APP_URL=https://公開URL` をGitHub Repository Variablesへ設定

## 必須Secret

- Stripe Sandbox: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID`, `STRIPE_WEBHOOK_SECRET`
- Portal: `STRIPE_PORTAL_CONFIGURATION_ID`
- SMTP: `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`

環境変数の値をGit、チャット、スクリーンショットへ貼らない。

## 本番化前

- PostgreSQLバックアップを有効化
- 独自ドメインとHTTPSを確認
- メール到達率と送信元ドメイン認証を確認
- Stripe Sandboxで支払い成功・失敗・期間末解約を再試験
- 法務、規約、プライバシー、特商法表示の確認

