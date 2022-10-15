from configparser import ConfigParser
from binance.client import Client
from tradingview_ta import TA_Handler, Interval, Exchange
import tradingview_ta

class trade_view:
    def __init__(self, stock, time):
        self.handler = TA_Handler(
            symbol= stock,
            exchange= "TWSE",
            screener= "TAIWAN",
            interval= time,
            timeout=None
            )
        self.analysis = self.handler.get_analysis()

if __name__ == '__main__':
    print(trade_view('2330', '1d').analysis)