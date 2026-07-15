import requests
from config import LINE_CHANNEL_ACCESS_TOKEN


def notify(message):

    url = "https://api.line.me/v2/bot/message/broadcast"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    body = {
        "messages": [
            {
                "type": "text",
                "text": message,
            }
        ]
    }

    r = requests.post(url, headers=headers, json=body)

    print(r.status_code)
    print(r.text)