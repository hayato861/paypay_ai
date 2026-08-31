from insight import create_insight
from market import get_market_data
from premium_report_web import create_premium_report_page
from scoring import recommend_courses, score_market


def main():
    data = get_market_data()
    market_score, reasons = score_market(data)
    ranking = recommend_courses(data, market_score)
    output = create_premium_report_page(
        data,
        market_score,
        ranking,
        reasons,
        create_insight(),
    )
    print(f"Premium report generated: {output}")


if __name__ == "__main__":
    main()

