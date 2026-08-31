from image import create_market_image
from logger import log
from notify import notify, notify_paid_member
from web import create_page
from x import create_x_post, save_x_draft


def publish(report, data, market_score, ranking, reasons, insight):
    print("=" * 40)
    print("📢 配信開始")
    print("=" * 40)

    try:
        create_page(data, market_score, ranking, reasons, insight)
        print("✅ WEB")
        log("WEB更新")
    except Exception as error:
        print("❌ WEB", error)
        log(f"WEBエラー: {error}")

    try:
        notify(report)
        print("✅ LINE")
        log("LINE送信")
    except Exception as error:
        print("❌ LINE", error)
        log(f"LINEエラー: {error}")

    image_path = None

    try:
        if market_score >= 85:
            stars = "★★★★★"
        elif market_score >= 70:
            stars = "★★★★☆"
        elif market_score >= 55:
            stars = "★★★☆☆"
        elif market_score >= 40:
            stars = "★★☆☆☆"
        else:
            stars = "★☆☆☆☆"

        image_path = create_market_image(
            market_score=market_score,
            stars=stars,
            top_course=ranking[0][0],
            top_score=ranking[0][1],
            qqq_change=data["change"],
            spy_change=data["spy_change"],
            vix=data["vix"],
        )
        print("✅ 画像生成:", image_path)
        log("市場レポート画像生成")
    except Exception as error:
        print("❌ 画像生成", error)
        log(f"画像生成エラー: {error}")

    try:
        x_text = create_x_post(data, market_score, ranking, insight)
        save_x_draft(x_text, image_path)
        print("✅ X手動投稿素材")
        log("X手動投稿素材生成")
    except Exception as error:
        print("❌ X手動投稿素材", error)
        log(f"X手動投稿素材エラー: {error}")

    print("=" * 40)
    print("配信完了")


def publish_premium(report, user_id, delivery_key):
    """Deliver a prepared premium report to one validated subscriber."""
    return notify_paid_member(report, user_id, delivery_key)
