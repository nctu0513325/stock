from Date_Trans import gen_backtesting_date_list, isweekend
from Select import Select, headers
from GA_distribute import GA_main
import re
import datetime
import requests
import pandas as pd
import time
from collections import defaultdict

def get_stock_price(stock, date):
    r = requests.get(f'https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=csv&date={date}&stockNo={stock}',headers=headers.my_headers)
    time.sleep(3)
    info = [l[:-1].replace('\"','').replace("-",'-1').replace("+",'1').split(",") for l in r.text.split("\r\n")[1:-13]]
    info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
    info_df = pd.DataFrame(info_dict)
    info_df[info_df.columns.tolist()].astype(float, errors='ignore')
    title = info_df.columns.tolist()        # ['日期', '收盤價']
    
    tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(date))    
    pattern = rf"(\d*)\/{tmp.group(2)}\/{tmp.group(3)}"
    info_df = info_df[title][info_df[title[0]].str.contains(pattern, regex = True)]
    
    return float(info_df[title[1]][0]) 
    
def backtesting_main(startdate, end_date, reselect_gap = 1):
    '''Backtesting if the strategy is Okay'''
    
    # parameter setting
    stock_code = []
    stock_buy = {}
    money_cash = 50000
    
    for date in gen_backtesting_date_list(startdate, end_date, reselect_gap):
        # date = [start_date_for_selection, end_date_for_selection, buy_stock_day]
        print(date)
        # test if buy_stock_day is on weekend to avoid no closing price
        time_tmp = re.search(r'(\d\d\d\d)(\d\d\d\d)', str(date[2]))
        while isweekend(date[2]) or time_tmp.group(2) == '0101' :
            tmp = datetime.datetime.strptime(str(date[2]), '%Y%m%d')
            tmp += datetime.timedelta(days=1)
            date[2] = int(datetime.datetime.strftime(tmp, '%Y%m%d'))
            time_tmp = re.search(r'(\d\d\d\d)(\d\d\d\d)', str(date[2]))
        
        while isweekend(date[0]):
            date[0] += 1
            
        # calculate money change
        money_today = money_cash
        for stock in stock_buy.keys():
            money_today += get_stock_price(stock, date[2]) * int(stock_buy[stock])
        
        # select stock and decide how to buy
        stock_code_new = Select(date[0], date[1])
        stock_buy_new = GA_main(stock_code_new, date[0], date[1], money_today)       
        
        print(stock_buy_new)
        # calculate new share of each stock 
        stock_buy_tmp = defaultdict(int)
        money_tmp = money_today
        for stock in stock_buy_new.keys():
            stock_close_price = get_stock_price(stock, date[2])
            money_on_stock = round(float(stock_buy_new[stock]) * money_today, 2)
            share_of_stock = int(money_on_stock/stock_close_price)
            stock_buy_tmp[stock] = share_of_stock
            money_tmp -= share_of_stock * stock_close_price
            print(f'stock :{stock}')
            print(f'share of stock : {share_of_stock}')
            print(f'money_today : {money_today}')
            print(f'stock close price :{stock_close_price}')
        
        money_cash = money_tmp
        stock_buy = stock_buy_new
                    
        print(f'done:{money_cash}')

if __name__ == '__main__':
    backtesting_main(20210101, 20211231, 1)