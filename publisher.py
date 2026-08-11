from notify import notify
from x import post
from web import create_page
from logger import log
from image import create_market_image


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

    # ========================================
    # WEB更新
    # ========================================

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


    # ========================================
    # LINE
    # ========================================

    try:

        notify(report)

        print("✅ LINE")
        log("LINE送信")

    except Exception as e:

        print("❌ LINE", e)
        log(f"LINEエラー: {e}")
        
    # ========================================
    # 市場レポート画像生成
    # ========================================

    image_path = None

    try:
        print("市場レポート画像生成開始")
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
            vix=data["vix"]
        )

        print("✅ 画像生成:", image_path)
        log("市場レポート画像生成")

    except Exception as e:
        print("❌ 画像生成", e)
        log(f"画像生成エラー: {e}")


    # ========================================
    # 市場レポート画像生成
    # ========================================

    try:

        print("市場レポート画像生成開始")

        # Web側と同じ星評価
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
            vix=data["vix"]
        )

        print("✅ 画像生成:", image_path)
        log("市場レポート画像生成")

    except Exception as e:

        print("❌ 画像生成", e)
        log(f"画像生成エラー: {e}")


    # ========================================
    # X
    # ========================================

    try:

        post(
            report,
            image_path
        )

        print("✅ X")
        log("X投稿")

    except Exception as e:

        print("❌ X", e)
        log(f"Xエラー: {e}")


    print("=" * 40)
    print("配信完了")