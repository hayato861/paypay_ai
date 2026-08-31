
# PayPay AI Morning Report

毎朝マーケットを分析し、
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
