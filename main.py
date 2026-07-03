from market import get_market_data
from signal import judge
from report import create_report
from history import save_history
from notify import notify

data = get_market_data()

stars, reasons, action = judge(data)

text = create_report(data, stars, reasons, action)

notify(text)

save_history(data, stars, reasons, action)