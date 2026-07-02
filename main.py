from market import get_market_data
from signal import judge
from report import create_report

data = get_market_data()

stars, reasons, action = judge(data)

text = create_report(data, stars, reasons, action)

print(text)