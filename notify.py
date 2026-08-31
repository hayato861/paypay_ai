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


def notify_paid_member(message, user_id, delivery_key=None):
    """Send one premium notification without exposing it to broadcast users.

    Subscription validation and idempotency must be completed by the member
    service before calling this function.
    """
    if not LINE_CHANNEL_ACCESS_TOKEN:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKENが設定されていません")
    if not user_id or not user_id.strip():
        raise ValueError("LINE user IDが必要です")

    body = {
        "to": user_id.strip(),
        "messages": [{"type": "text", "text": message}] if isinstance(message, str) else [message],
    }
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    if delivery_key:
        headers["X-Line-Retry-Key"] = delivery_key

    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=body,
        timeout=15,
    )
    response.raise_for_status()
    return response
