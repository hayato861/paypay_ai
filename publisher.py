from notify import notify
from x import post
from web import create_page
from logger import log

def publish(report):

    print("=" * 40)
    print("📢 配信開始")
    print("=" * 40)

    try:
        notify(report)
        print("✅ LINE")
        log("LINE更新")
    except Exception as e:
        print("❌ LINE", e)
        log(f"LINEエラー: {e}")

    try:
        post(report)
        print("✅ X")
    except Exception as e:
        print("❌ X", e)
        log(f"Xエラー: {e}")

    try:
        create_page(report)
        print("✅ WEB")
        log("WEB更新")
    except Exception as e:
        print("❌ WEB", e)
        log(f"WEBエラー: {e}")

    print("=" * 40)
    print("配信完了")