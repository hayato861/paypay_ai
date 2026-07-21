from pathlib import Path

def create_page(report):

    Path("public").mkdir(exist_ok=True)

    html=f"""
<!DOCTYPE html>

<html lang="ja">

<head>

<meta charset="UTF-8">

<title>PayPay AI</title>

</head>

<body>

<pre>

{report}

</pre>

</body>

</html>
"""

    with open("public/index.html","w",encoding="utf-8") as f:

        f.write(html)

    print("Webページ更新")