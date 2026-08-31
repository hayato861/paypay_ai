
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
