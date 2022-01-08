import os, re
import numpy as np
import csv
import time
import sqlite3
from Daily import Sel_Company
from Date_Trans import trans_time_for_db
# ============== parameter setting ===============
NUM_CHROME = 100            
Pc = 0.5    				# 交配率 (代表共執行Pc*NUM_CHROME/2次交配)
Pm = 0.5   					# 突變率 (代表共要執行Pm*NUM_CHROME*Num_of_Job次突變)
pressure = 0.1              # N-tourment 參數
best_iteration = []                         #紀錄多快達到已知最佳解
first = 0

NUM_PARENT = NUM_CHROME                         # 父母的個數
Num_pressure = int(pressure * NUM_CHROME)       
NUM_CROSSOVER = int(Pc * NUM_CHROME / 2)        # 交配的次數
NUM_CROSSOVER_2 = NUM_CROSSOVER*2               # 上數的兩倍
# NUM_MUTATION = int(Pm * NUM_CHROME * Num_of_Job)   # 突變的次數
np.random.seed(0)

candi_company_dic = {'2493': '宏普', '2616': '永裕', '6184': '新產', '2324': '嘉彰', '3528': '敦吉', '2347': '國票金', '1615': '伸興', '2904': '和碩'}
start_date = '20201201'
end_date = '20201231'
money = 50000
# ============== function ==================
def  init_pop(NUM_BIT) :
    '''Initialize population'''
    tmp = np.random.randint(10,size = (NUM_CHROME, NUM_BIT))
    tmp = [i/sum(i) for i in tmp]
    return tmp

def get_close_from_db(company, date):
    print('pass')
    
def fitFunc(num_list):
    '''fit function, calculate total money earn'''
    money_earn = 0
    for i in len(num_list):
        close_start = get_close_from_db(company_code[i], trans_time_for_db(start_date))
        close_end = get_close_from_db(company_code[i], trans_time_for_db(end_date))
        num_of_stock = int(money*num_list[i]/close_start)
        money_earn += num_of_stock*(close_end - close_start)
    return money_earn
            
def evaluatePop(pop):
    '''get list of fitness of each pop'''
    return [fitFunc(i) for i in pop]
        

def GA_main(candi_company_dic, start_date, end_date):
    global company_code 
    company_code = [i for i in candi_company_dic.keys()]
    NUM_BIT = len(company_code)
    
    pop = init_pop(NUM_BIT)         # initialize population
    pop_fit = evaluatePop(pop)      #calculate fitness

if __name__ == '__main__':
    GA_main(candi_company_dic)