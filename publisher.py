from notify import notify
from x import post
from web import create_page
from logger import log

print("publisher.py が呼ばれました")


def publish(
    report,
    data,
    market_score,
    ranking,
    reasons,
    insight
):

    print("=" * 40)
    print("📢 配信開始")
    print("=" * 40)

    # WEB更新
    try:
        print("create_page 開始")

        create_page(
            data,
            market_score,
            ranking,
            reasons,
            insight
        )

        print("create_page 終了")

        print("✅ WEB")
        log("WEB更新")
    except Exception as e:
        print("❌ WEB", e)
        log(f"WEBエラー: {e}")

    # LINE
    try:
        notify(report)
        print("✅ LINE")
        log("LINE送信")
    except Exception as e:
        print("❌ LINE", e)
        log(f"LINEエラー: {e}")

    # X
    try:
        post(report)
        print("✅ X")
        log("X投稿")
    except Exception as e:
        print("❌ X", e)
        log(f"Xエラー: {e}")

    print("=" * 40)
    print("配信完了")