from market import get_market_data
from signal import score_market, recommend_courses
from report import create_report
from notify import notify

# 市場データ取得
data = get_market_data()

# 市場スコア計算
market_score, reasons = score_market(data)

# おすすめランキング作成
ranking = recommend_courses(
    data,
    market_score
)



# レポート作成
text = create_report(
    data,
    market_score,
    reasons,
    ranking
)

print(text)

notify(text)