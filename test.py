from Date_Trans import time_for_yahoo, headers
import requests, sqlite3
import yfinance as yf
import pandas as pd
import json

# msft = yf.Ticker("2330.TW")
period_1, period_2 = time_for_yahoo(20231018, 20241018)
r = requests.get(f'https://query1.finance.yahoo.com/v8/finance/chart/2330.TW?period1={period_1}&period2={period_2}&interval=1d&events=history&includeAdjustedClose=true' ,headers=headers.my_headers)
info_dict = json.loads(r.text)
print(info_dict['chart']['result'][0]['timestamp'])

info_df = pd.DataFrame(info_dict['indicators'])
info_df[info_df.columns.tolist()].astype(float, errors='ignore')
# print(info_df)
db = sqlite3.connect(f'20231018_20241018.db')
info_df.to_sql(f'daily_2003', db, if_exists='append', index=False)
# info = [l.split(",") for l in r.text.split("\n")]
# print(info)
# info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
# print(info_dict)
