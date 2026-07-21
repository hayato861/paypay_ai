from datetime import datetime

def log(message):

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/system.log","a",encoding="utf-8") as f:

        f.write(f"{now} {message}\n")