import requests
import pandas as pd
import re, os
import time
from collections import defaultdict
from Date_Trans import date_trans, time_for_yahoo
import sqlite3

"""Get daily stock data, and list all stock matched with requirements"""
    
def regexp_db( expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

def Select(start, end, gap) :        
    """Get data from twse. select company"""
    date_list_week = date_trans(start, end, gap)
    all_company = []           # each item is a list stored company 
    all_company_code = []      # each item is a list stored company code
    candi_company_dic = {}     # {$code : $name} for company matched with requirement
    try:
        os.mkdir("daily_data")
    except:
        pass
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
    
    """Get data from twse. select PE for 本益比, Yeild for  殖利率, PB for 淨值比"""
    for date in date_list_week:
        # print(f'Collecting {date} data from website')
        try:                
            # get data from website and transfer into dataframe
            requests.adapters.DEFAULT_RETRIES = 5
            time.sleep(3)  # set sleep time to avoid connection error
            r = requests.get(f'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={date}&selectType=ALL', headers = my_headers)
            requests.session().keep_alive = False
            info = [l[:-1].replace('\"','').replace("-",'-1').replace("+",'1').split(",") for l in r.text.split("\r\n")[1:-13]]
            info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
            info_df = pd.DataFrame(info_dict)
            info_df[info_df.columns.tolist()].astype(float, errors='ignore')
            title = info_df.columns.tolist()    #['證券代號', '證券名稱', '殖利率(%)', '股利年度', '本益比', '股價淨值比', '財報年/季']

            # set stock choosing requirement
            info_df = info_df[pd.to_numeric(info_df[title[4]],errors = 'ignore') < 15 ]     #本益比
            info_df = info_df[pd.to_numeric(info_df[title[2]],errors = 'ignore') > 4 ]      #殖利率(%)
            info_df = info_df[pd.to_numeric(info_df[title[5]],errors = 'ignore') < 2 ]      #股價淨值比
            
            tmp = []
            for com_name in info_df['證券名稱']:
                tmp.append(com_name)
            all_company.append(tmp)
            
            tmp = []
            for com_code in info_df['證券代號']:
                tmp.append(com_code)
            all_company_code.append(tmp)
            
            info_df.to_csv(f'daily_data/{date}.csv', encoding = 'utf_8_sig')
        except IndexError:
            print(f'{date} is holiday, no data.')
            
    candi_company = list(set(all_company[0]).intersection(*all_company[1:]))
    candi_company_code = list(set(all_company_code[0]).intersection(*all_company_code[1:]))
    candi_company_dic = dict(zip(candi_company_code, candi_company))
    print(len(candi_company))
    print(candi_company_dic)

    """Get closing price from twse and sel by closing price > ave(60) ave(120) """
    clos_price_all = defaultdict(list)      # store only last day close price for every month
    ave_close_price_60 = defaultdict(list)
    ave_close_price_120 = defaultdict(list)
    candi_company = []
    company_code_tmp =[]
    period_1, period_2 = time_for_yahoo(start, end)
    tmp_time = re.search(r'(\d\d\d\d)(\d\d\d\d)', str(start))
    year = tmp_time.group(1)
    try:
        os.remove(f'{year}_each_company.db')
    except:
        pass
    
    for company_code in candi_company_code:
        r = requests.get(f'https://query1.finance.yahoo.com/v7/finance/download/{company_code}.TW?period1={period_1}&period2={period_2}&interval=1d&events=history&includeAdjustedClose=true' ,headers=my_headers)
        info = [l.split(",") for l in r.text.split("\n")]
        info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
        info_df = pd.DataFrame(info_dict)
        info_df[info_df.columns.tolist()].astype(float, errors='ignore')
        
        # store data in sqlite to select data 
        db = sqlite3.connect(f'{year}_each_company.db')
        cursor = db.cursor()
        info_df.to_sql(f'daily_{company_code}', db, if_exists='append', index=False)
        db.commit()
        db.create_function("REGEXP", 2, regexp_db)
        sqlite3.enable_callback_tracebacks(True)
        
        # store monthly data in list
        for month in range(1,13):
            # average 60 day data
            if month > 11:
                pass
            else:
                cursor.execute(f'SELECT avg(Close) FROM daily_{company_code} WHERE Date REGEXP ?', [f'\d\d\d\d-0[{str(month)},{str(month+1)}]-\d\d'])
                result = cursor.fetchall()
                ave_close_price_60[company_code].append(float(result[-1][0]))
            # average 120 day data
            if month > 9:
                pass
            else:
                cursor.execute(f'SELECT avg(Close) FROM daily_{company_code} WHERE Date REGEXP ?', [f'\d\d\d\d-0[{str(month)},{str(month+1)},{str(month+2)},{str(month+3)}]-\d\d'])
                result = cursor.fetchall()
                ave_close_price_120[company_code].append(float(result[-1][0]))
            # close price for the last day in every month
            cursor.execute(f'SELECT Close FROM daily_{company_code} WHERE Date REGEXP ?', [f'\d\d\d\d-{str(month).zfill(2)}-\d\d'])
            result = cursor.fetchall()
            clos_price_all[company_code].append(float(result[-1][0]))
        db.close()     # close connection with sqlite
        
        # close - ave close <-5%*close
        pass_flag = 1
        # ave 60:
        for i in range(len(ave_close_price_60[company_code])):
            if (clos_price_all[company_code][i+1] - ave_close_price_60[company_code][i]) < -(clos_price_all[company_code][i+1]*0.05):
                pass_flag = 0
            if pass_flag == 0:
                break
        # ave 120:        
        for i in range(len(ave_close_price_120[company_code])):
            if (clos_price_all[company_code][i+3] - ave_close_price_120[company_code][i]) < -(clos_price_all[company_code][i+3]*0.05):
                pass_flag = 0
            if pass_flag == 0:
                break 
        
        if pass_flag:
            company_code_tmp.append(company_code)
            candi_company.append(candi_company_dic[company_code])
        
    candi_company_code = company_code_tmp
    candi_company_dic = dict(zip(candi_company_code, candi_company))
    print(len(candi_company))
    print(candi_company_dic)
    return candi_company_dic
        
if __name__ == '__main__':
    candi_company_dic = Select(20200102, 20201231, 7)
