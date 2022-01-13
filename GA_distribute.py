import os, re
import numpy as np
import csv
import time
import sqlite3

# ============== parameter setting ===============
NUM_CHROME = 10           
Pc = 0.5    				# 交配率 (代表共執行Pc*NUM_CHROME/2次交配)
Pm = 0.5   					# 突變率 (代表共要執行Pm*NUM_CHROME*Num_of_Job次突變)
pressure = 0.1              # N-tourment 參數
best_iteration = []                         #紀錄多快達到已知最佳解
iteration = 100
first = 0

NUM_PARENT = NUM_CHROME                         # 父母的個數
Num_pressure = int(pressure * NUM_CHROME)       
NUM_CROSSOVER = int(Pc * NUM_CHROME / 2)        # 交配的次數
NUM_CROSSOVER_2 = NUM_CROSSOVER*2               # 上數的兩倍
# NUM_MUTATION = int(Pm * NUM_CHROME * Num_of_Job)   # 突變的次數
np.random.seed(0)

candi_company_dic = {'2493': '宏普', '2616': '永裕', '6184': '新產', '2324': '嘉彰', '3528': '敦吉', '2347': '國票金', '1615': '伸興', '2904': '和碩'}
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

def get_close_from_db(company, start_date, end_date):
    '''close the the first and the last close price for the last month'''
    db = sqlite3.connect(f'{start_date}_{end_date}.db')
    cursor = db.cursor()
    time_tmp = re.search(r'(\d\d\d\d)(\d\d)(\d\d)', str(end_date))
    last_month = time_tmp.group(2)
    
    db.create_function("REGEXP", 2, regexp_db)
    cursor.execute(f'SELECT Close FROM daily_{company} WHERE Date REGEXP ?', [f'\d\d\d\d-{str(last_month)}-\d\d'])
    result = cursor.fetchall()
    db.close()
    return float(result[0][0]), float(result[-1][0])
    
def fitFunc(num_list):
    '''fit function, calculate total money earn'''
    money_earn = 0
    for i in range(len(num_list)):
        print(f'num_list : {num_list}')
        close_start, close_end = get_close_from_db(company_code[i], start_date, end_date)
        split_money = i/sum(num_list)*money
        num_of_stock = int(split_money/close_start)       # num of stock can buy 
        money_earn += num_of_stock*(close_end - close_start)    # money can earn 
    return money_earn
            
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
        pass

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
 
def GA_main(candi_company_dic, start, end):
    global company_code, start_date, end_date, NUM_BIT, NUM_MUTATION
    start_date, end_date = start, end
    company_code = [i for i in candi_company_dic.keys()]
    NUM_BIT = len(company_code)    
    NUM_MUTATION = int(Pm * NUM_CHROME * NUM_BIT)
    
    pop = init_pop(NUM_BIT)         # initialize population
    print(pop)
    pop_fit = evaluatePop(pop)      #calculate fitness
    
    for i in range(iteration):
        print(f'Iteration : {i}')
        parent, parent_fit = selection(pop, pop_fit)
        offspring = crossover(parent, parent_fit)
        mutation(offspring)
        # print(f'offspring:{offspring}')
        # print(f'offspring_len:{len(offspring)}')
        offspring_fit = evaluatePop(offspring)
        pop, pop_fit = replace(pop, pop_fit, offspring, offspring_fit)
        print(f'Best solution : {pop_fit[0]}')
        # =============pass===========

if __name__ == '__main__':
    GA_main(candi_company_dic, start, end)