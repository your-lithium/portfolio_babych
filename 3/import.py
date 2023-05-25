# набір потрібних для імпорту вихідних даних:
# посилання на сторінки, назви для кінцевих файлів, xpath заголовків, орієнтовна кількість сторінок для досягнення бажаної кількості слововживань
link_nv = "https://nv.ua/ukr/world.html"
output_file_nv = "nv.txt"
xpath_nv = '//*[@class="title "]/text()'
number_nv = 100
link_hromadske = "https://hromadske.ua/svit"
output_file_hromadske = "hromadske.txt"
xpath_hromadske = '//*[@class="TopicPostList"]//a/@data-vr-contentbox'
number_hromadske = 500

# імпортування потрібних бібліотек
import requests
from lxml import html
from termcolor import colored

# зчитування заголовків зі сторінок сайту, запис їх до списку
print(colored("\nProcess initialised.\n", "green"))
articles_headers = []
for i in range(number_hromadske):
    web_page = requests.get(link_hromadske + "?page=" + str(i + 1))
    tree = html.fromstring(web_page.content)
    [articles_headers.append(header) for header in tree.xpath(xpath_hromadske)]
print(colored("\nHeaders read.\n", "green"))

# запис вивантажених заголовків до текстового файлу
with open(output_file_hromadske, "w", encoding="windows-1251") as f:
    for header in articles_headers:
        try:
            f.write(header + "\n")
        except UnicodeEncodeError:
            continue
print(colored("\nFile created.\n", "green"))
