from insight import create_insight
from market import get_market_data
from premium_report_web import create_premium_report_page
from scoring import recommend_courses, score_market
from clock import now_jst
import member_store as store


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
    store.initialize()
    store.save_premium_report(
        now_jst().strftime("%Y-%m-%d"),
        output.read_text(encoding="utf-8"),
    )
    print(f"Premium report generated: {output}")
    print("Premium report saved to member database")


if __name__ == "__main__":
    main()
