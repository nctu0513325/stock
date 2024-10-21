import re, os, time, sqlite3, requests
import pandas as pd
from collections import defaultdict
from trade_view import trade_view
from Date_Trans import gen_date_list, time_for_yahoo, headers
from GA_distribute import GA_main

"""Get daily stock data, and list all stock matched with requirements"""
    
def regexp_db( expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

def Select(start, end, gap = 7) :        
    """Get data from twse. select company"""
    print(f'Start:{start} End:{end}')
    date_list = gen_date_list(start, end, gap)
    all_company_code = []      # each item is a list stored company code
    
    """Get data from twse. select PE for 本益比, Yeild for  殖利率, PB for 淨值比"""
    for date in date_list:
        # print(f'Current Select Day :{date}')
        # print(f'Collecting {date} data from website')
        try:                
            # get data from website and transfer into dataframe
            requests.adapters.DEFAULT_RETRIES = 5
            time.sleep(3)  # set sleep time to avoid connection error
            r = requests.get(f'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={date}&selectType=ALL', headers = headers.my_headers)
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
            for com_code in info_df['證券代號']:
                tmp.append(com_code)
            all_company_code.append(tmp)
            
        except IndexError:
            print(f'{date} is holiday, no data.')
    print(all_company_code)
    candi_company_code = list(set(all_company_code[0]).intersection(*all_company_code[1:]))

    """Get closing price from twse and sel by closing price > ave(60) ave(120) """
    company_code_tmp =[]
    period_1, period_2 = time_for_yahoo(start, end)
    
    if os.path.exists(f'{start}_{end}.db'):
        os.remove(f'{start}_{end}.db')
    
    # EMA_50, EMA_100 < close, RSI_7d < 20,  RSI_7d > RSI_30d
    print(candi_company_code)
    for company_code in candi_company_code:
        company_data = trade_view(company_code, '1d').analysis
        EMA_50  = company_data.indicators['EMA50']
        EMA_100 = company_data.indicators['EMA100']
        close   = company_data.indicators['close']
        RSI_7d  = trade_view(company_code, '1W').analysis.indicators['RSI']
        RSI_30d = trade_view(company_code, '1M').analysis.indicators['RSI']
        print(f'Company:{company_code}, EMA50:{EMA_50}, EMA100:{EMA_100}, Close:{close}')
        
        if (close > 0.95*EMA_100) and (close > 0.95*EMA_50) and (RSI_7d > 20) and (RSI_7d > RSI_30d):
            company_code_tmp.append(company_code)
            
            # Save history data for GA
            r = requests.get(f'https://query1.finance.yahoo.com/v7/finance/download/{company_code}.TW?period1={period_1}&period2={period_2}&interval=1d&events=history&includeAdjustedClose=true' ,headers=headers.my_headers)
            info = [l.split(",") for l in r.text.split("\n")]
            info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
            info_df = pd.DataFrame(info_dict)
            info_df[info_df.columns.tolist()].astype(float, errors='ignore')
            
            db = sqlite3.connect(f'{start}_{end}.db')
            info_df.to_sql(f'daily_{company_code}', db, if_exists='append', index=False)
        
    candi_company_code = company_code_tmp
    print(candi_company_code)
    return candi_company_code
          
if __name__ == '__main__':
    start = 20231018
    end = 20241018
    candi_company_code = Select(start, end, 7)
    # candi_company_code = ['5546', '2303', '2603', '2006']

    
    for i in range(10):
        GA_main(candi_company_code, str(start), str(end), 800000)