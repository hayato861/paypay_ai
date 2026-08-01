import requests
from config import LINE_CHANNEL_ACCESS_TOKEN


def notify(message):

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
        json=body
    )

    print(r.status_code)
    print(r.text)