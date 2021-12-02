import requests
import pandas as pd
import re, os
import time
from collections import defaultdict
from io import StringIO
from Date_Trans import date_trans
# from fake_useragent import UserAgent

class Sel_Company():
    """Get daily stock data, and list all stock matched with requirements"""
    
    def __init__(self, start, end, gap):
        self.start = start
        self.end = end
        self.gap = gap
        self.daily_data = []
        self.all_company = []           # each item is a list stored company 
        self.all_company_code = []      # each item is a list stored company code
        self.candi_company_dic = {}     # {$code : $name} for company matched with requirement

    def Select(self):
        
        """Get data from twse. select PE for 本益比, Yeild for  殖利率, PB for 淨值比"""
        self.date_list_week, self.date_list_month = date_trans(self.start, self.end, self.gap)
        try:
            os.mkdir("daily_data")
        except:
            pass
        my_headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                    "Accept-Encoding": "gzip, deflate, br", 
                    "Accept-Language": "zh-TW,zh;q=0.9", 
                    "Host": "www.twse.com.tw",  #目標網站
                    "Sec-Fetch-Dest": "document", 
                    "Sec-Fetch-Mode": "navigate", 
                    "Sec-Fetch-Site": "none", 
                    "Upgrade-Insecure-Requests": "1", 
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36", #使用者代理
                    "Referer": "https://www.google.com/"  #參照位址
                }
        for date in self.date_list_week:
            print(date)
            try:                
                # get data from website and transfer into dataframe
                requests.adapters.DEFAULT_RETRIES = 5
                time.sleep(5)  # set sleep time to avoid connection error
                requests.session().keep_alive = False
                r = requests.get(f'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={date}&selectType=ALL', headers = my_headers)
                info = [l[:-1].replace('\"','').replace("-",'-1').replace("+",'1').split(",") for l in r.text.split("\r\n")[1:-13]]
                info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
                info_df = pd.DataFrame(info_dict)
                
                # r = request.post(f'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={date}&selectType=ALL', headers = my_headers )
                # info_df = pd.read_csv(StringIO(r.text.replace("=", "")[1:]), 
                #             header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
                # info_df = info_df.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"), errors='ignore'))
                
                # info = request.urlopen(request.Request(f'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={date}&selectType=ALL', headers = my_headers))
                # print(info.read())
                # info = [l[:-1].replace('\"','').replace("-",'-1').replace("+",'1').split(",") for l in info.read().decode('utf-8').split("\r\n")[1:-13]]
                # info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
                # info_df = pd.DataFrame(info_dict)
                title = info_df.columns.tolist()    #['證券代號', '證券名稱', '殖利率(%)', '股利年度', '本益比', '股價淨值比', '財報年/季']
                
                print(title)
                print(info_df)

                # set stock choosing requirement
                info_df = info_df[pd.to_numeric(info_df[title[4]],errors = 'ignore') < 15 ]     #本益比
                info_df = info_df[pd.to_numeric(info_df[title[2]],errors = 'ignore') > 4 ]      #殖利率(%)
                info_df = info_df[pd.to_numeric(info_df[title[5]],errors = 'ignore') < 2 ]      #股價淨值比
                
                tmp = []
                for com_name in info_df['證券名稱']:
                    tmp.append(com_name)
                self.all_company.append(tmp)
                
                tmp = []
                for com_code in info_df['證券代號']:
                    tmp.append(com_code)
                self.all_company_code.append(tmp)
                
                info_df.to_csv(f'daily_data/{date}.csv', encoding = 'utf_8_sig')
            except IndexError:
                print(f'{date} is holiday, no data.')
                self.date_list_week.remove(date)
            # except ValueError:
            #     print(f'{date} is holiday, no data.')
            #     self.date_list_week.remove(date)
                
        self.candi_company = list(set(self.all_company[0]).intersection(*self.all_company[1:]))
        self.candi_company_code = list(set(self.all_company_code[0]).intersection(*self.all_company_code[1:]))
        self.candi_company_dic = dict(zip(self.candi_company_code, self.candi_company))
        print(len(self.candi_company))
        print(self.candi_company)
    
    
        """Get closing price from twse and sel by closing price > ave(60) ave(120) """
        clos_price_all = defaultdict(list)
        for date in self.date_list:
            for company_code in self.candi_company_dic.keys():
                # get each company's closing for all year
                requests.adapters.DEFAULT_RETRIES = 5
                time.sleep(5)
                r = requests.get(f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv&date={date}&stockNo={company_code}', headers = my_headers)
                info = [l[:-1].replace('\"','').replace("-",'-1').replace("+",'1').split(",") for l in r.text.split("\r\n")[1:-13]]
                info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
                info_df = pd.DataFrame(info_dict)
                
                # store closing price in dictionary
                clos_price_all[company_code].append(num for num in list(pd.to_numeric(info_df['收盤價'], error = 'ignore')))
        
                
                
if __name__ == '__main__':
    D = Sel_Company(20200102, 20201231, 7)
    D.Select()
