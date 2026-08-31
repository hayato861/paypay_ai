from pathlib import Path

from clock import now_jst

def log(message):
    
    Path("logs").mkdir(exist_ok=True)

    now = now_jst().strftime("%Y-%m-%d %H:%M:%S JST")

    with open("logs/system.log","a",encoding="utf-8") as f:

        f.write(f"{now} {message}\n")
