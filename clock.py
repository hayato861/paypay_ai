from datetime import datetime
from zoneinfo import ZoneInfo


JST = ZoneInfo("Asia/Tokyo")


def now_jst():
    """Return the current timezone-aware time in Japan."""
    return datetime.now(JST)

