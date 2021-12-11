import re

def date_trans(start, end, gap) -> list : 
    """Trans time into list to avoid wrong date."""
    big_month = [1, 3, 5, 7, 8, 10, 12]
    small_month = [4, 6, 9, 11]
    time_list_week = []
    time_list_month = []
    
    while int(start) <= int(end):           
        date_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(start))
        year = int(date_tmp.group(1))
        month = int(date_tmp.group(2))
        day = int(date_tmp.group(3))
        
        if f'{str(year).zfill(4)}{str(month).zfill(2)}01' not in time_list_month:
            time_list_month.append(f'{str(year).zfill(4)}{str(month).zfill(2)}01')
        
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
    
    
        
    return time_list_week, time_list_month
