import numpy as np
import matplotlib.pyplot as plt
import scipy

H_YEAR = 8760 - 2920
weeks = 40 #weeks of work in a year
workweek = 45 #hours of work in a week
commute = 90 #commute time in a day

def create_array(table_num):
    if table_num > 9:
                filepath = f'NC_Census_2021/table{table_num}.csv'
    else:
        filepath = f'NC_Census_2021/table0{table_num}.csv'
    my_array = np.genfromtxt(filepath, dtype = float, 
                             delimiter = ",", skip_header=1)
    return my_array

table_nums = [1, 2, 7, 9, 11]

# age_path = 'NC_Census_2021/table01.csv'
# disability_path = 'NC_Census_2021/table02.csv'
# income_path = 'NC_Census_2021/table07.csv'
# commute_path = 'NC_Census_2021/table09.csv'
# transit_path = 'NC_Census_2021/table10.csv'
# worktime_path = 'NC_Census_2021/table11.csv'

age = create_array(1)
disability = create_array(2)
income = create_array(7)
commute = create_array(9)
transit = create_array(10)
worktime = create_array(11)

age_aggr = np.zeros((np.shape(age)[0], 25))
disability_aggr = np.zeros((np.shape(disability)[0], 8))
income_aggr = np.zeros((np.shape(income)[0], 22))
worktime_aggr = np.zeros((np.shape(income)[0], 21))

ages = [2.5, 7, 12, 16, 18.5, 20, 21, 23, 27, 32, 37, 42, 47, 52, 57, 60.5, 63, 65.5, 68, 72, 77, 82, 92.5]
disabilities = [2.5, 11, 25, 49.5, 69.5, 85]
incomes = [1225, 3750, 6250, 8750, 11125, 13750, 16250, 18750, 21125, 23750, 27500, 32500, 37500, 42500, 47500, 52500, 60000, 70000, 87500, 150000]
workhours = [45 * 51, 45 * 48.5, 45 * 43.5, 45 * 33, 45 * 20, 45 * 7, 24.5 * 51, 24.5 * 48.5, 24.5 * 43.5, 24.5 * 33, 24.5 * 20, 24.5 * 7, 7.5 * 51, 7.5 * 48.5, 7.5 * 43.5, 7.5 * 33, 7.5 * 20, 7.5 * 7, 0]

age_aggr[:, 0: 2] = age[:, 0: 2]
disability_aggr[:, 0: 2] = disability[:, 0: 2]
income_aggr[:, 0: 2] = income[:, 0: 2]
worktime_aggr[:, 0: 2] = worktime[:, 0: 2]

age_aggr[:, 2: 26] = age[:, 3:26] + age[:, 26:49]

for j in range(0, 18, 3):
    disability_aggr[:, int(j/3 + 2)] = (disability[:, j + 4] + disability[:, j + 23])/(disability[:, j + 3] + disability[:, j + 22])

for l in range(20):
    income_aggr[:, l + 2] = income[:, l + 3] + income[:, l + 24]
    
worktime_indices = [5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25]
t = 0
for p in worktime_indices:
    worktime_aggr[:, t + 2] = worktime[:, p] + worktime[:, p + 24]
    t += 1

disabilities_expected = np.zeros((np.shape(age)[0], 3))
disabilities_expected[:, 0: 2] = disability[:, 0: 2]
disabilities_sum = 0
for i in range(np.shape(disability_aggr)[0]):
    loc = disability_aggr[i, 2:9]
    disabilities_expct = np.dot(loc, disabilities)/disabilities_expected[i,1]
    disabilities_expected[i, 2] = disabilities_expct

ages_expected = np.zeros((np.shape(age)[0], 3))
ages_expected[:, 0: 2] = age[:, 0: 2]
age_sum = 0
for i in range(np.shape(age_aggr)[0]):
    loc = age_aggr[i, 2:26]
    age_expct = np.dot(loc, ages)/ages_expected[i,1]
    ages_expected[i, 2] = age_expct

income_expected = np.zeros((np.shape(income)[0], 3))
income_expected[:, 0: 2] = income[:, 0: 2]
income_sum = 0
for k in range(np.shape(income_aggr)[0]):
    loc = income_aggr[k, 2:23]
    income_expct = np.dot(loc, incomes)/income_expected[k,1]
    income_expected[k, 2] = income_expct

worktime_expected = np.zeros((np.shape(income)[0], 3))
worktime_expected[:, 0: 2] = worktime[:, 0: 2]
worktime_sum = 0
for m in range(np.shape(worktime_aggr)[0]):
    loc = worktime_aggr[m, 2:22]
    worktime_expct = np.dot(loc, workhours)/worktime_expected[m,1]
    worktime_expected[m, 2] = worktime_expct

print(worktime_expected)

def mobility(disability, age):
    return np.exp(-1/(disability(1 - age^2)))

def free_time(hours_year, weeks, workweek, commute):
    return hours_year/(1 + np.exp(weeks * (workweek + commute * 5)))

