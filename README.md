
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
`ADS_ENABLED=true`、`ADSENSE_CLIENT`、`ADSENSE_SLOT` の3項目を設定した場合だけ表示される。
有料LINE通知にはbroadcastを使わず、契約状態を確認した会員ごとにpush APIを使用する。
