from datetime import datetime
from pathlib import Path

def log(message):
    
    Path("logs").mkdir(exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/system.log","a",encoding="utf-8") as f:

        f.write(f"{now} {message}\n")