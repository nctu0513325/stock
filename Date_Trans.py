import re
import datetime
import pandas as pd

def time_for_yahoo(start_time, end_time):
    """Yahoo website need time with special form"""
    # https://chenchenhouse.com/python002/
    initial_time_str = datetime.datetime.strptime( '1970-01-01' , '%Y-%m-%d' )
    
    start_time_str = datetime.datetime.strptime( str(start_time) , '%Y%m%d' )
    start_time_str -= datetime.timedelta(days=1)
    
    end_time_str = datetime.datetime.strptime( str(end_time) , '%Y%m%d' )
    
    return (start_time_str - initial_time_str).days * (24 * 60 * 60 ) + 22411, (end_time_str - initial_time_str).days * (24 * 60 * 60 ) + 22411

def isweekend(date):
    '''test if the date is weekend'''
    date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(date))
    date_str = f'{date_tmp.group(1)}-{date_tmp.group(2)}-{date_tmp.group(3)}'
    weekday = pd.Timestamp(date_str)
    
    if weekday.dayofweek == 6 or weekday.dayofweek == 5:
        return 1
    else :
        return 0
    
def gen_date_list(start, end, gap):
    '''gen date list for greping data from twse'''    
    date_str_start = datetime.datetime.strptime(str(start), '%Y%m%d')
    date_str_end = datetime.datetime.strptime(str(end), '%Y%m%d')
    
    date_list = []
    date_list.append(date_str_start.strftime('%Y%m%d'))
    
    while date_str_start < date_str_end:
        # add day gap
        date_str_start += datetime.timedelta(days=gap)
        date_list.append(date_str_start.strftime('%Y%m%d'))
    
    return date_list

def gen_backtesting_date_list(startdate, enddate, reselection_gap):
    date_list = []          
    while (startdate + 60 )< enddate:       # +60 avoid month gap error
        #[start_date_for_selection, end_date_for_selection, buy_stock_day]        
        # selection start day => one year before buy_stock_day
        date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(startdate))
        start_date_for_sel = int(f'{int(date_tmp.group(1))-1}{date_tmp.group(2)}{date_tmp.group(3)}')
        
        # selection end day => one day before buy_stock_day
        end_date_for_sel = datetime.datetime.strptime(str(startdate), '%Y%m%d')
        end_date_for_sel -= datetime.timedelta(days=1)
        end_date_for_sel = int(end_date_for_sel.strftime('%Y%m%d'))
        
        date_list.append([start_date_for_sel, end_date_for_sel, startdate])
        
        # next buy stock day => startdate += reselection_gap
        next_month = (int(date_tmp.group(2))+reselection_gap) % 12
        if next_month  == 0:
            next_month = 12
        startdate = int(f'{date_tmp.group(1)}{str(next_month).zfill(2)}{date_tmp.group(3)}')
    
    return date_list
