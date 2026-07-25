from market import get_market_data
from signal import score_market, recommend_courses
from report import create_report
from publisher import publish
from grader import grade
from history import save_history

def main():
    
    grade()

    data = get_market_data()

    market_score, reasons = score_market(data)

    ranking = recommend_courses(data, market_score)

    save_history(
        market_score,
        ranking[0][0]
    )

    text = create_report(
        data,
        market_score,
        reasons,
        ranking
    )

    print(text)

    publish(text)


if __name__ == "__main__":
    main()