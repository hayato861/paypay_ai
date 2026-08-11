from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_market_image(
    market_score,
    stars,
    top_course,
    top_score,
    qqq_change,
    spy_change,
    vix
):

    width = 1200
    height = 675

    image = Image.new(
        "RGB",
        (width, height),
        "#0f172a"
    )

    draw = ImageDraw.Draw(image)

    # フォント
    font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
    small_font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

    try:
        title_font = ImageFont.truetype(
            font_path,
            52
        )

        score_font = ImageFont.truetype(
            font_path,
            100
        )

        normal_font = ImageFont.truetype(
            small_font_path,
            32
        )

        small_font = ImageFont.truetype(
            small_font_path,
            25
        )

    except Exception:
        title_font = ImageFont.load_default()
        score_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # タイトル
    draw.text(
        (70, 55),
        "📈 PayPay AI",
        font=title_font,
        fill="#f8fafc"
    )

    draw.text(
        (75, 120),
        "Morning Market Report",
        font=small_font,
        fill="#94a3b8"
    )

    # 市場スコア
    draw.text(
        (75, 190),
        "MARKET SCORE",
        font=small_font,
        fill="#94a3b8"
    )

    draw.text(
        (70, 225),
        str(market_score),
        font=score_font,
        fill="#38bdf8"
    )

    draw.text(
        (300, 275),
        stars,
        font=normal_font,
        fill="#facc15"
    )

    # おすすめカード
    draw.rounded_rectangle(
        (650, 180, 1125, 380),
        radius=25,
        fill="#1e293b"
    )

    draw.text(
        (685, 210),
        "🥇 TODAY'S PICK",
        font=small_font,
        fill="#94a3b8"
    )

    draw.text(
        (685, 255),
        top_course,
        font=normal_font,
        fill="#f8fafc"
    )

    draw.text(
        (685, 305),
        f"{top_score} points",
        font=normal_font,
        fill="#22c55e"
    )

    # 市場データ
    draw.text(
        (75, 470),
        f"QQQ  {qqq_change:+.2f}%",
        font=normal_font,
        fill="#f8fafc"
    )

    draw.text(
        (350, 470),
        f"S&P500  {spy_change:+.2f}%",
        font=normal_font,
        fill="#f8fafc"
    )

    draw.text(
        (700, 470),
        f"VIX  {vix:.2f}",
        font=normal_font,
        fill="#f8fafc"
    )

    draw.text(
        (75, 590),
        "Powered by PayPay AI",
        font=small_font,
        fill="#64748b"
    )

    # 保存
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    output = output_dir / "market_report.png"

    image.save(
        output,
        quality=95
    )

    print("画像保存:", output)

    return output