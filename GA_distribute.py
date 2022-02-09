from cmath import sqrt
import re
import numpy as np
import time
import sqlite3
from decimal import Decimal
import decimal
from collections import defaultdict

# ============== parameter setting ===============
NUM_CHROME = 100        
Pc = 0.5    				# 交配率 (代表共執行Pc*NUM_CHROME/2次交配)
Pm = 0.5   					# 突變率 (代表共要執行Pm*NUM_CHROME*Num_of_Job次突變)
pressure = 0.1              # N-tourment 參數
iteration = 3000

NUM_PARENT = NUM_CHROME                         # 父母的個數
Num_pressure = int(pressure * NUM_CHROME)       
NUM_CROSSOVER = int(Pc * NUM_CHROME / 2)        # 交配的次數
NUM_CROSSOVER_2 = NUM_CROSSOVER*2               # 上數的兩倍
# np.random.seed(0)

stock_num = 4
# 2020
candi_company_code = ['1615', '2493', '2616', '2324', '2904', '2347', '6184']
# 2021
# candi_company_code = ['2890', '1101', '9945', '2812', '6192', '2546', '2838', '6671', '4722', '1712', '1323', '2820', '1726', '2459', '2891', '5522', '8131', '1604', '3209', '2887', '6184', '2885']
start = '20200101'
end = '20201231'
# ============== function ==================
def  init_pop() :
    '''Initialize population'''
    pop =[]
    tmp = np.zeros(NUM_BIT, int)
    pnt = np.random.choice(NUM_BIT, num_of_stock)
    for _ in range(NUM_CHROME):
        for i in pnt:
            tmp[i] = np.random.randint(low = 1, high = 10, size = 1)[0]
        pop.append(tmp)

    return pop
    # return np.random.randint(10,size = (NUM_CHROME, NUM_BIT))

def regexp_db( expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

def get_close_from_db(company, month):
    '''close the the first and the last close price for the last month'''
    cursor = db.cursor()
    
    db.create_function("REGEXP", 2, regexp_db)
    cursor.execute(f'SELECT Close FROM daily_{company} WHERE Date REGEXP ?', [f'\d\d\d\d-{str(month).zfill(2)}-\d\d'])
    result = cursor.fetchall()

    return Decimal(result[0][0]).quantize(Decimal('0.0000'), rounding=decimal.ROUND_HALF_UP), \
            Decimal(result[-1][0]).quantize(Decimal('0.0000'), rounding=decimal.ROUND_HALF_UP)
    
def fitFunc(num_list):
    '''fit function, calculate total money earn'''
    fit = 0
    
    for i in range(len(num_list)):
        part = Decimal(f'{num_list[i]/sum(num_list)}').quantize(Decimal('0.0000'), rounding=decimal.ROUND_HALF_UP)
        if part == 0:
            pass        # avoid Value error
        else:            
            # calculate total money_earn
            close_start, close_end = last_month_closing[company_code[i]][0], last_month_closing[company_code[i]][1]
            money_de = Decimal(f'{money}')
            split_money = Decimal(f'{part*money_de}').quantize(Decimal('0.0000'), rounding=decimal.ROUND_HALF_UP)
            num_of_stock = round(split_money/close_start, 0)       # num of stock can buy 
            money_earn = num_of_stock*(close_end - close_start)    # money can earn
            
            # calculate average SD
            ave_SD = part * Decimal(f"{annual_SD_company[company_code[i]][0]}")
        
            fit += money_earn/ave_SD
            
    return float(money_earn/(ave_SD**2))
            
def evaluatePop(pop):
    '''get list of fitness of each pop'''
    return [fitFunc(i) for i in pop]

def selection(pop, pop_fit):
    '''Use N-tourment to select parent group'''
    a, b = [], []
    
    for _ in range(NUM_PARENT):
        fit_select = np.random.choice(NUM_CHROME, Num_pressure, replace = False)
        best = np.max([pop_fit[i] for i in fit_select])
        a.append(pop[pop_fit.index(best)])
        b.append(pop_fit[pop_fit.index(best)])
        
    return a, b

def crossover(parent, parent_fit):
    ''' Use N-tourment to select parent again,
        exchange first and third non-zero number'''
        
    child = []
    
    for _ in range(NUM_CROSSOVER):
        # N-tourment select parent
        fit_select = np.random.choice(NUM_CHROME, Num_pressure, replace = False)
        best = np.max([parent_fit[i] for i in fit_select])
        parent_1 = parent[parent_fit.index(best)]
        non_zero_1 = np.where(parent_1 != 0)        # find the index of non_zero number
        
        fit_select = np.random.choice(NUM_CHROME, Num_pressure, replace = False)
        best = np.max([parent_fit[i] for i in fit_select])
        parent_2 = parent[parent_fit.index(best)]
        non_zero_2 = np.where(parent_2 != 0)        # find the index of non_zero number
        
        # exchange first and third non_zero number
        for i in range(len(non_zero_1)):
            parent_1[non_zero_1[i]], parent_2[non_zero_2[i]] = parent_2[non_zero_2[i]], parent_1[non_zero_1[i]]
            
        child.append(parent_2)
        child.append(parent_1)
    
    return child
    
def mutation(offspring):
    for _ in range(NUM_MUTATION):
        off_sel = np.random.randint(len(offspring), size = 1)[0]   # random select offspring
        change_zero_index = np.random.choice(np.where(offspring[off_sel] == 0)[0], int(stock_num/2))        # find zero index
        change_non_zero_index = np.random.choice(np.where(offspring[off_sel] != 0)[0], int(stock_num/2))    # find non-zero index
        for i in range(len(change_non_zero_index)):
            offspring[off_sel][change_non_zero_index[i]], offspring[off_sel][change_zero_index[i]] = \
            offspring[off_sel][change_zero_index[i]], offspring[off_sel][change_non_zero_index[i]]

def sortChrome(pop, pop_fit):
    '''sort the chrome according to fit decending'''
    pop_index = range(len(pop))
    pop_fit, pop_index = zip(*sorted(zip(pop_fit, pop_index), reverse=True))
    
    return [pop[i] for i in pop_index], pop_fit

def replace(pop, pop_fit, offspring, offspring_fit):
    '''replace old pop with new offspring with better fit'''
    tmp = np.concatenate((pop, offspring), axis = 0)
    tmp_fit = pop_fit + offspring_fit
    
    tmp, tmp_fit = sortChrome(tmp, tmp_fit)
    
    return tmp[:NUM_CHROME], list(tmp_fit[:NUM_CHROME])

def Annual_SD_cal(com_code):
    '''Calculate annual_SD of each stock'''
    annual_SD = defaultdict(list)
    monthly_SD = defaultdict(list)
    for code in com_code:
        for month in range(1,13):
            month_start, month_end = get_close_from_db(code, month)            
            monthly_SD[code].append((month_end - month_start) / month_start)
        company_SD = np.std(np.array(monthly_SD[code]), ddof = 1)
        annual_SD[code].append(sqrt((company_SD**2)*12).real)
        
    return annual_SD

def get_last_month_close(com_code):
    '''store last month closing price for each company'''
    last_closing = defaultdict(list)
    for code in com_code:
        last_month_1, last_month_2 = get_close_from_db(code, last_month)
        last_closing[code].append(last_month_1)
        last_closing[code].append(last_month_2)
    
    return last_closing
 
def GA_main(candi_company_code, start, end, invest_money):
    # Initialize parameter
    start_time = time.process_time()
    global company_code, start_date, end_date, NUM_BIT, NUM_MUTATION, db, last_month, last_month_closing, annual_SD_company, num_of_stock, money
    start_date, end_date, company_code, money = start, end, candi_company_code, invest_money
    NUM_BIT = len(company_code)
    NUM_MUTATION = int(Pm * NUM_CHROME * NUM_BIT)
    db = sqlite3.connect(f'{start_date}_{end_date}.db')
    time_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(end_date))
    last_month = time_tmp.group(2)
    annual_SD_company = Annual_SD_cal(candi_company_code)           # store ASD in list for faster data reading
    last_month_closing = get_last_month_close(candi_company_code)   # store last month closing price for each company for faster data reading
    
    # invest 4 stock at most
    if NUM_BIT > 4 :
        num_of_stock = 4 
    else :
        num_of_stock = NUM_BIT
        
    pop = init_pop()         # initialize population
    pop_fit = evaluatePop(pop)      #calculate fitness
    
    for i in range(iteration):
        #print(f'Iteration : {i}')
        parent, parent_fit = selection(pop, pop_fit)
        offspring = crossover(parent, parent_fit)
        mutation(offspring)
        offspring_fit = evaluatePop(offspring)
        pop, pop_fit = replace(pop, pop_fit, offspring, offspring_fit)
        
    # print(f'pop:{pop[0]} pop_fit:{pop_fit[0]}')
    stop_time = time.process_time()
    # print(f'time : {stop_time-start_time}')
    
    stock_distribute = defaultdict(float)
    for i in range(len(company_code)):
        stock_distribute[company_code[i]] = pop[0][i]/sum(pop[0])
    
    db.close()
    
    # return money distribution on each stock ( dict )
    print(stock_distribute)
    return stock_distribute

if __name__ == '__main__':
    GA_main(candi_company_code, start, end, 50000)
