# імпортування потрібних бібліотек
import sqlite3
from math import sqrt
from collections import Counter
from tabulate import tabulate

# під'єднання до БД, визначення команд для зчитування даних
con = sqlite3.connect('../frequencies.db')
cur = con.cursor()
select_from_pos_freqs_nv = f'''SELECT freq_01, freq_02, freq_03, freq_04,
                                         freq_05, freq_06, freq_07, freq_08,
                                         freq_09, freq_10, freq_11, freq_12,
                                         freq_13, freq_14, freq_15, freq_16,
                                         freq_17, freq_18, freq_19, freq_20
                                         from pos_freqs_nv
                                         WHERE pos = ?'''
select_from_pos_freqs_hromadske = f'''SELECT freq_01, freq_02, freq_03, freq_04,
                                         freq_05, freq_06, freq_07, freq_08,
                                         freq_09, freq_10, freq_11, freq_12,
                                         freq_13, freq_14, freq_15, freq_16,
                                         freq_17, freq_18, freq_19, freq_20
                                         from pos_freqs_hromadske
                                         WHERE pos = ?'''

# визначення початкових даних для обчислення та аналізу Xi-квадрату
xi_pos = ["Іменник", "Дієслово", 'Дієслово "бути"', "Сполучник сурядності", "Сполучник підрядності"]
freed_xi = (20 - 1) * (2 - 1)
print("Кількість ступенів свободи: " + str(freed_xi))
comp_value_xi = 30.1
print("Критичне значення Xi-квадрату (дов. ім.= 95%): " + str(comp_value_xi))

# обчислення та аналіз Хі-квадрату
for pos in xi_pos:
    cur.execute(select_from_pos_freqs_nv, (pos,))
    nv = cur.fetchone()
    cur.execute(select_from_pos_freqs_hromadske, (pos,))
    hrom = cur.fetchone()

    sum_nv = sum(nv)
    sum_hrom = sum(hrom)
    n = sum_nv + sum_hrom

    final_sums = []
    for i, freq in enumerate(nv):
        sq_freq_nv = freq**2
        sq_freq_hrom = hrom[i]**2
        sum_k = freq + hrom[i]
        final_sums.append(sq_freq_nv / (sum_k * sum_nv))
        final_sums.append(sq_freq_hrom / (sum_k * sum_hrom))

    xi = n * (sum(final_sums) - 1)
    print('Xi-квадрат для частини мови "' + pos + '": ' + str(xi))

    # виведення до консолі лінгвостатистичної інтерпретації результатів
    if xi < comp_value_xi:
        print("Показник Xi-квадрату менше критичного значення. Розходження між порівнюваними вибірками неістотне.")
    elif xi == comp_value_xi:
        print("Показник Xi-квадрату дорівнює критичному значенню. Розходження між порівнюваними вибірками неістотне.")
    else:
        print("Показник Xi-квадрату більше критичного значення. Розходження між порівнюваними вибірками істотне.")
    print()
print()


# визначення початкових даних для обчислення та аналізу критерію Стьюдента
st_pos = ["Прикметник", "Прислівник", "Прийменник"]
freed_st = 20 + 20 - 2
print("Кількість ступенів свободи: " + str(freed_st))
comp_value_st = 2.04
print("Критичне значення критерію Стьюдента (дов. ім.= 95%): " + str(comp_value_st))

# обчислення та аналіз критерію Стьюдента
for pos in st_pos:
    cur.execute(select_from_pos_freqs_nv, (pos,))
    nv = cur.fetchone()
    cur.execute(select_from_pos_freqs_hromadske, (pos,))
    hrom = cur.fetchone()

    nv_c = dict(Counter(nv))
    hrom_c = dict(Counter(hrom))

    sum_nv = sum(nv)
    sum_hrom = sum(hrom)

    avg_nv = sum_nv/20
    avg_hrom = sum_hrom/20

    num = abs(avg_nv - avg_hrom)

    top_sum_nv = 0
    for k, v in nv_c.items():
        top_sum_nv += ((k - avg_nv) ** 2) * v
    top_sum_hrom = 0
    for k, v in hrom_c.items():
        top_sum_hrom += ((k - avg_hrom) ** 2) * v
    top_den_1 = top_sum_nv + top_sum_hrom
    den_1 = top_den_1 / (20 + 20 - 2)

    den_2 = (20 + 20) / (20 * 20)

    denom = sqrt(den_1 * den_2)

    t = num/denom
    print('Критерій Стьюдента для частини мови "' + pos + '": ' + str(t))

    # виведення до консолі лінгвостатистичної інтерпретації результатів
    if t < comp_value_st:
        print("Критерій Стьюдента менше критичного значення. Розходження у частоті між порівнюваними вибірками неістотне.")
    elif t == comp_value_st:
        print("Критерій Стьюдента дорівнює критичному значенню. Розходження у частоті між порівнюваними вибірками неістотне.")
    else:
        print("Критерій Стьюдента більше критичного значення. Розходження у частоті між порівнюваними вибірками істотне.")
        l = (t - comp_value_st) / t
        print("Відносне розходження (ступінь розходження): " + str(l))

        print(tabulate([['nv', "\\", t], ['hromadske', l, "\\"]], headers=['Sample', 'nv', 'hromadske']))
    print()
