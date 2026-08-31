import requests
from config import LINE_CHANNEL_ACCESS_TOKEN


def notify(message):

    if not LINE_CHANNEL_ACCESS_TOKEN:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKENが設定されていません")

    url = "https://api.line.me/v2/bot/message/broadcast"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # 文字列ならテキスト送信
    if isinstance(message, str):

        body = {
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

    # dictならFlex Message送信
    else:

        body = {
            "messages": [
                message
            ]
        }

    r = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=15,
    )

    r.raise_for_status()
    print(f"LINE送信成功: HTTP {r.status_code}")
    return r
