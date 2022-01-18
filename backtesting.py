from Date_Trans import gen_backtesting_date_list, isweekend

def backtesting_main(startdate, end_date, reselect_gap = 1):
    gen_backtesting_date_list(startdate, end_date, reselect_gap)


if __name__ == '__main__':
    backtesting()