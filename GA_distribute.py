from cmath import sqrt
import re
from unicodedata import decimal
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
best_iteration = []                         #紀錄多快達到已知最佳解
iteration = 3000
first = 0

NUM_PARENT = NUM_CHROME                         # 父母的個數
Num_pressure = int(pressure * NUM_CHROME)       
NUM_CROSSOVER = int(Pc * NUM_CHROME / 2)        # 交配的次數
NUM_CROSSOVER_2 = NUM_CROSSOVER*2               # 上數的兩倍
np.random.seed(0)

candi_company_code = ['2493', '2616', '6184', '2324', '3528', '2347', '1615', '2904']
start = '20200102'
end = '20201231'
money = 50000
# ============== function ==================
def  init_pop(NUM_BIT) :
    '''Initialize population'''
    return np.random.randint(10,size = (NUM_CHROME, NUM_BIT))

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
            pass
        else:            
            # calculate total money_earn
            close_start, close_end = last_month_closing[company_code[i]][0], last_month_closing[company_code[i]][1]
            split_money = Decimal(f'{part*money}').quantize(Decimal('0.0000'), rounding=decimal.ROUND_HALF_UP)
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
    
    for i in range(NUM_PARENT):
        fit_select = np.random.choice(NUM_CHROME, Num_pressure, replace = False)
        best = np.max([pop_fit[i] for i in fit_select])
        a.append(pop[pop_fit.index(best)])
        b.append(pop_fit[pop_fit.index(best)])
        
    return a, b

def crossover(parent, parent_fit):
    ''' Use N-tourment to select parent again,
        and do one point crossover'''
        
    child = []
    
    for _ in range(NUM_CROSSOVER):
        fit_select = np.random.choice(NUM_CHROME, Num_pressure, replace = False)
        best = np.max([parent_fit[i] for i in fit_select])
        parent_1 = parent[parent_fit.index(best)]
        
        fit_select = np.random.choice(NUM_CHROME, Num_pressure, replace = False)
        best = np.max([parent_fit[i] for i in fit_select])
        parent_2 = parent[parent_fit.index(best)]
        
        cut_point = np.random.randint(1, NUM_BIT)
        
        child.append(list(np.concatenate((parent_1[0:cut_point], parent_2[cut_point:NUM_BIT]), axis = 0 )))
        child.append(list(np.concatenate((parent_2[0:cut_point], parent_1[cut_point:NUM_BIT]), axis = 0 )))
    
    return child
    
def mutation(offspring):
    for _ in range(NUM_MUTATION):
        num_point = []
        off_sel = np.random.randint(len(offspring), size = 1)[0]   # random select offspring
        num_point = np.random.choice(NUM_BIT, np.random.randint(low = 1, high = NUM_BIT/2, size = 1)[0])        # decide the num of point to change
        for n in num_point:
            offspring[off_sel][n] = np.random.randint(10, size = 1)[0]
        
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
    '''Calculate annual_SD of each stock
    https://reurl.cc/KppLr9'''
    annual_SD = defaultdict(list)
    monthly_SD = defaultdict(list)
    for code in com_code:
        for month in range(1,13):
            month_start, month_end = get_close_from_db(code, month)            
            monthly_SD[code].append((month_end - month_start) / month_start)
        company_SD = np.std(np.array(monthly_SD[code]), ddof = 1)
        print(f'company_code:{company_SD}')
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
 
def GA_main(candi_company_code, start, end):
    # Initialize parameter
    start_time = time.process_time()
    global company_code, start_date, end_date, NUM_BIT, NUM_MUTATION, db, last_month, last_month_closing, annual_SD_company
    start_date, end_date, company_code = start, end, candi_company_code 
    NUM_BIT = len(company_code)
    NUM_MUTATION = int(Pm * NUM_CHROME * NUM_BIT)
    db = sqlite3.connect(f'{start_date}_{end_date}.db')
    time_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(end_date))
    last_month = time_tmp.group(2)
    annual_SD_company = Annual_SD_cal(candi_company_code)
    print(annual_SD_company)
    last_month_closing = get_last_month_close(candi_company_code)
    
    pop = init_pop(NUM_BIT)         # initialize population
    pop_fit = evaluatePop(pop)      #calculate fitness
    
    for i in range(iteration):
        print(f'Iteration : {i}')
        parent, parent_fit = selection(pop, pop_fit)
        offspring = crossover(parent, parent_fit)
        mutation(offspring)
        offspring_fit = evaluatePop(offspring)
        pop, pop_fit = replace(pop, pop_fit, offspring, offspring_fit)
        
    print(f'pop:{pop[0]} pop_fit:{pop_fit[0]}')
    db.close()
    stop_time = time.process_time()
    print(f'time : {stop_time-start_time}')

if __name__ == '__main__':
    GA_main(candi_company_code, start, end)