import requests
import pandas as pd
import re, os
import time
from collections import defaultdict

class Sel_Candi_Company():
    """Get daily stock data, and list all stock matched with requirements"""
    
    def __init__(self, start, end, gap):
        self.start = start
        self.end = end
        self.gap = gap
        self.daily_data = []
        self.all_company = []           # each item is a list stored company 
        self.all_company_code = []      # each item is a list stored company code
        self.candi_company_dic = {}     # {$code : $name} for company matched with requirement
        
    def date_trans(self) -> list : 
        """Trans time into list to avoid wrong date."""
        big_month = [1, 3, 5, 7, 8, 10, 12]
        small_month = [4, 6, 9, 11]
        time_list = []
        
        while int(self.start) <= int(self.end):           
            date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(self.start))
            year = int(date_tmp.group(1))
            month = int(date_tmp.group(2))
            day = int(date_tmp.group(3))
            
            if (month in big_month) and (day > 31):
                month += 1
                day = day - 31
            elif (month in small_month) and (day > 30):
                month += 1
                day = day - 30
            elif (month == 2):
                if (int(year) % 4 == 0) and (day > 29):
                    month += 1
                    day = day - 29
                elif (int(year) % 4 != 0) and (day > 28):
                    month += 1
                    day = day - 28
            if (month > 12):
                year += 1
                month = 1
            time_list.append(f'{str(year).zfill(4)}{str(month).zfill(2)}{str(day).zfill(2)}')
            day += self.gap
            self.start = f'{str(year).zfill(4)}{str(month).zfill(2)}{str(day).zfill(2)}'
            
        return time_list    

    def Sel_by_PE_Yeild_PB(self):
        """Get data from twse. PE for 本益比, Yeild for  殖利率, PB for 淨值比"""
        self.date_list = self.date_trans()
        try:
            os.mkdir("daily_data")
        except:
            pass
        for date in self.date_list:
            try:                
                # get data from website and transfer into dataframe
                requests.adapters.DEFAULT_RETRIES = 5
                time.sleep(5)
                my_headers={'user-agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
                r = requests.get(f'https://www.twse.com.tw/exchangeReport/BWIBBU_d?response=csv&date={date}&selectType=ALL', headers = my_headers)
                info = [l[:-1].replace('\"','').replace("-",'-1').replace("+",'1').split(",") for l in r.text.split("\r\n")[1:-13]]
                info_dict = {z[0] : list(z[1:]) for z in zip(*info)}
                info_df = pd.DataFrame(info_dict)
                title = info_df.columns.tolist()    #['證券代號', '證券名稱', '殖利率(%)', '股利年度', '本益比', '股價淨值比', '財報年/季']
                
                # set stock choosing requirement
                info_df = info_df[pd.to_numeric(info_df[title[4]],errors = 'ignore') < 15 ] #本益比
                info_df = info_df[pd.to_numeric(info_df[title[2]],errors = 'ignore') > 4]   #殖利率(%)
                info_df = info_df[pd.to_numeric(info_df[title[5]],errors = 'ignore') < 2]   #股價淨值比
                
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
                self.date_list.remove(date)
                
        self.candi_company = list(set(self.all_company[0]).intersection(*self.all_company[1:]))
        self.candi_company_code = list(set(self.all_company_code[0]).intersection(*self.all_company_code[1:]))
        self.candi_company_dic = dict(self.candi_company_code, self.candi_company)
        print(len(self.candi_company))
        print(self.candi_company)
    
    def Sel_by_Closing_Price(self):
        """Get closing price from twse and sel by closing price > ave(60) ave(120) """
        clos_price_all = defaultdict(list)
        for date in self.date_list:
            for company_code in self.candi_company_dic.keys():
                # get each company's closing for all year
                requests.adapters.DEFAULT_RETRIES = 5
                time.sleep(5)
                my_headers={'user-agent': '"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
                r = requests.get(f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv&date={date}&stockNo={company_code}', headers = my_headers)
                   
                
if __name__ == '__main__':
    D = Sel_Candi_Company(20200101, 20201231, 7)
    D.Sel_by_PE_Yeild_PB()
