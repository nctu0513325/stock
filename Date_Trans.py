import re
import datetime

def date_trans(start, end, gap) -> list : 
    """Trans time into list to avoid wrong date."""
    big_month = [1, 3, 5, 7, 8, 10, 12]
    small_month = [4, 6, 9, 11]
    time_list_week = []
    
    while int(start) <= int(end):           
        date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(start))
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
        time_list_week.append(f'{str(year).zfill(4)}{str(month).zfill(2)}{str(day).zfill(2)}')
        day += gap
        start = f'{str(year).zfill(4)}{str(month).zfill(2)}{str(day).zfill(2)}'
        
    return time_list_week

def time_for_yahoo(start_time, end_time):
    """Yahoo website need time with special form"""
    # https://chenchenhouse.com/python002/
    initial_time_str = datetime.datetime.strptime( '1970-01-01' , '%Y-%m-%d' )
    
    date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(start_time))
    start_time_str = f'{date_tmp.group(1)}-{date_tmp.group(2)}-{date_tmp.group(3)}'
    start_time_str = datetime.datetime.strptime( str(start_time_str) , '%Y-%m-%d' )
    
    date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(end_time))
    end_time_str = f'{date_tmp.group(1)}-{date_tmp.group(2)}-{date_tmp.group(3)}'
    end_time_str = datetime.datetime.strptime( str(end_time_str) , '%Y-%m-%d' )
    
    period_1 = (start_time_str - initial_time_str).days * (24 * 60 * 60 ) + 22411
    period_2 = (end_time_str - initial_time_str).days * (24 * 60 * 60 ) + 22411
    
    return period_1, period_2
