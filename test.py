import imp
from Date_Trans import gen_date_list,gen_backtesting_date_list, is_trade_day
import requests
import pandas as pd
import os, re
import sqlite3
import numpy as np
from GA_distribute import Annual_SD_cal
from datetime import datetime
# from Select import Select
import tushare
from backtesting import get_stock_price

# print(datetime.today().weekday())
# https://www.delftstack.com/zh-tw/howto/python/python-datetime-day-of-week/#:~:text=%E5%B9%BE%E7%9A%84%E5%90%8D%E7%A8%B1%E3%80%82-,%E4%BD%BF%E7%94%A8%20weekday()%20%E6%96%B9%E6%B3%95%E5%9C%A8Python%20%E4%B8%AD%E7%8D%B2%E5%8F%96%E6%97%A5%E6%9C%9F%E6%98%AF,%E7%82%BA0%EF%BC%8C%E9%80%B1%E6%97%A5%E7%82%BA6%E3%80%82
# print(time_for_yahoo_back(20210118))

# get_stock_price(2330, 20200102)
# https://blog.csdn.net/lvluobo/article/details/90635655
get_stock_price(2330, 20210301)