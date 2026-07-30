from market import get_market_data
from signal import score_market, recommend_courses
from report import create_report
from publisher import publish
from grader import grade
from history import *
from insight import create_insight

def main():
    
    grade()

    data = get_market_data()
    market_score, reasons = score_market(data)
    ranking = recommend_courses(data, market_score)

    save_history(
        market_score,
        ranking[0][0]
    )

    insight = create_insight()

    text = create_report(
        data,
        market_score,
        reasons,
        ranking,
        insight
    )

    print(text)
    
    print(reasons)
    
    publish(
    text,
    data,
    market_score,
    ranking,
    reasons,
    insight
)

    print(load_history())
    print(yesterday_diff())
    print(average_score())
    print(highest_score())
    print(lowest_score())

if __name__ == "__main__":
    main()