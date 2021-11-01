import numpy as np
import requests
from io import StringIO
import pandas as pd
import re, os

class Daily():
    """Get daily stock data."""
    
    def __init__(self, start, end, gap):
        self.start = start
        self.end = end
        self.gap = gap
        self.daily_data = []
        
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

    def get_data(self):
        """Get data from twse."""
        date_list = self.date_trans()
        try:
            os.mkdir("daily_data")
        except:
            pass
        for date in date_list:
            try:
                r = requests.post(f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={date}&type=ALL')
                df = pd.read_csv(StringIO(r.text.replace("=", "")), 
                            header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
                df = df.apply(lambda s: pd.to_numeric(s.astype(str).str.replace(",", "").replace("+", "1").replace("-", "-1"), errors = 'ignore'))
                df = df[df['本益比'] < 15 ]
                df.to_csv(f'daily_data/{date}.csv')
            except ValueError:
                print(f'{date} is holiday, no data.')
                
if __name__ == '__main__':
    D = Daily(20210907, 20210907, 7)
    D.get_data()
