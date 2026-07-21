from pathlib import Path

def post(report):

    Path("logs").mkdir(exist_ok=True)

    with open("logs/x_post.txt","w",encoding="utf-8") as f:

        f.write(report)

    print("X投稿内容を保存しました")