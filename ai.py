from openai import OpenAI
from config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)


def ai_judge(data):

    prompt = f"""
あなたは長期積立投資のアドバイザーです。

以下のデータから、
PayPay資産運用で今日おすすめのコースを選んでください。

候補

・NASDAQ100
・S&P500
・全世界株式
・ゴールド
・新興国株式

市場データ

QQQ価格:{data["price"]}

QQQ前日比:{data["change"]:.2f}%

S&P500:{data["spy_change"]:.2f}%

VIX:{data["vix"]:.2f}

25日線:{data["ma25"]:.2f}

75日線:{data["ma75"]:.2f}

必ずJSONだけ返してください。

{
    "course":"",
    "confidence":90,
    "reason":"",
    "comment":""
}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    text = response.output_text

    return json.loads(text)