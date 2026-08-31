# 会員アプリ公開手順（無料検証構成）

`render.yaml`は、課金事故を避けるためRenderの無料Webサービスだけを作る。Render Cronは最低月1ドル、
Render無料PostgreSQLは作成30日後に失効するため、どちらもBlueprintには含めない。

## 無料構成

- 会員Web: Render Free Web Service（15分無通信で休止）
- 会員DB: 外部の無料PostgreSQL。接続文字列をRenderの`DATABASE_URL`へ設定
- レポート生成: `.github/workflows/premium_report.yml`（平日9:20 JST）
- ログインメール: HTTPSで送れるResend。Render無料WebではSMTPポートを利用できない
- 決済: Stripe Sandboxのみ。実課金は開始しない

無料枠には停止・容量・転送量等の制限があり、本番有料サービスの恒久構成ではない。

## Renderへデプロイ

1. 外部PostgreSQLを作り、SSL対応の接続文字列を控える
2. RenderでこのGitHubリポジトリの`render.yaml`をBlueprintとして読み込む
3. 未同期の環境変数を設定する
4. `https://公開URL/healthz`と`https://公開URL/`を確認する
5. Stripe Sandboxに`https://公開URL/stripe/webhook`を登録する
6. Stripeが発行した署名シークレットを`STRIPE_WEBHOOK_SECRET`へ設定する

## Renderの必須環境変数

- `DATABASE_URL`: 外部PostgreSQL接続文字列
- Stripe Sandbox: `STRIPE_SECRET_KEY`, `STRIPE_PRICE_ID`, `STRIPE_WEBHOOK_SECRET`
- Portal: `STRIPE_PORTAL_CONFIGURATION_ID`
- Resend: `RESEND_API_KEY`, `EMAIL_FROM`（認証済み送信元）

`ALLOW_STRIPE_LIVE=false`は維持する。Secretの値はGit、チャット、スクリーンショットへ貼らない。

## GitHubの設定

Repository Secretに`MEMBER_DATABASE_URL`として、同じPostgreSQL接続文字列を登録する。
Repository Variableの`MEMBER_APP_URL`にはRenderの公開URLを登録する。
Actionsの`Premium report`を手動実行し、会員画面でレポートが読めることを確認する。

## 本番化前

- 有料の永続DBとバックアップへ移行
- 独自ドメイン、メール送信元ドメイン、監視を設定
- Stripe Sandboxで支払い成功・失敗・期間末解約を再試験
- 法務、利用規約、プライバシー、特商法表示を確認
