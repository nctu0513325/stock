from Date_Trans import time_for_yahoo
import requests

period_1, period_2 = time_for_yahoo(20200101, 20201231)
print(period_1,period_2)

# https://query1.finance.yahoo.com/v7/finance/download/" + stock_id + "?period1=" + str(s1) + "&amp;period2=" + str(s2) + "&amp;interval=1d&amp;events=history&amp;includeAdjustedClose=true"