# імпортування потрібних бібліотек
import os

# визначення початкових даних: назви цільових папок та вихідних файлів
nv_folder = r'nv'
hromadske_folder = r'hromadske'
nv_file = "nv.txt"
hromadske_file = "hromadske.txt"

# створення нової папки у поточній директорії
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, hromadske_folder)
if not os.path.exists(final_directory):
   os.makedirs(final_directory)

# зчитування вихідного файлу із заголовками
with open(hromadske_file, "r", encoding="windows-1251") as handle:
   headers = handle.readlines()

# підрахунок обсягу (у рядках/заголовках) підвибірок (рівно 1/20) від кількості рядків(заголовків)
if len(headers)%20 == 0:
   sample_size = len(headers)/20
else:
   sample_size = len(headers)//20 + 1

# функція для створення поділеного на визначені за обсягом підсписки списку
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# поділ вихідного файлу, запис 20 нових файлів-підвибірок
samples = chunks(headers, sample_size)
for i, sample in enumerate(samples):
   with open("{}/sample{}.txt".format(hromadske_folder, i+1), "w") as handle:
      handle.writelines(sample)
