from Date_Trans import time_for_yahoo
import requests
import pandas as pd
import os, re
import sqlite3

period_1, period_2 = time_for_yahoo(20200101, 20201231)
print(period_1,period_2)
my_headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                    "Accept-Encoding": "gzip, deflate, br", 
                    "Accept-Language": "zh-TW,zh;q=0.9", 
                    "Sec-Fetch-Dest": "document", 
                    "Sec-Fetch-Mode": "navigate", 
                    "Sec-Fetch-Site": "none", 
                    "Upgrade-Insecure-Requests": "1", 
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36", #使用者代理
                    "Referer": "https://www.google.com/"  #參照位址
                }

r = requests.get(f'https://query1.finance.yahoo.com/v7/finance/download/2330.TW?period1={period_1}&period2={period_2}&interval=1d&events=history&includeAdjustedClose=true' ,headers=my_headers)
info = [l.split(",") for l in r.text.split("\n")]
info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
info_df = pd.DataFrame(info_dict)
print(info_df)

def regexp_db(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

# trans to sqlite to select data
db = sqlite3.connect("2020.db")
cursor = db.cursor()
# cursor.execute(f'CREATE TABLE 2330')
db.commit()
info_df.to_sql('2330', db, if_exists='append', index=False)
db.create_function("REGEXP", 2, regexp_db)
print(info_df)
sqlite3.enable_callback_tracebacks(True)   # <-- !

date = '01'
code = '2330'
cursor.execute(f'SELECT Close FROM "{code}" WHERE Date REGEXP ?', [f'\d\d\d\d-{date}-\d\d'])
# db.execute('select error()')
result = cursor.fetchall()
print(result)
for item in result:
    print(type(str(item)))
    print(str(item[0]))
db.close()


# https://query1.finance.yahoo.com/v7/finance/download/" + stock_id + "?period1=" + str(s1) + "&amp;period2=" + str(s2) + "&amp;interval=1d&amp;events=history&amp;includeAdjustedClose=true"
