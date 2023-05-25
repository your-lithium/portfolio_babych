import re, pymorphy2

morph = pymorphy2.MorphAnalyzer(lang='uk')


def transgressives(verb):
    sya_bool = False
    if re.fullmatch("[\w']+с[яь]", verb) is not None:
        sya_bool = True
        verb = verb[:-2]

    p = morph.parse(verb)
    for i in range(len(p)):
        if p[i].tag.POS == "VERB":
            p = p[i]
            break
    aspect = p.tag.aspect

    if aspect == "impf":
        transgressive = p.inflect({"3per", "plur", "pres"}).word[:-2] + "чи"
    else:
        transgressive = p.inflect({"masc", "past"}).word + "ши"

    if sya_bool is True:
        transgressive += "сь"
    return transgressive


file_name = input("Вкажіть назву вашого файлу: ")
if len(file_name) < 1:
    file_name = "words.csv"
with open(file_name) as file:
    lines = file.readlines()

lines.pop(0)
transgressives_list = []
for line in lines:
    line = (line.strip(";\n")).split(";")
    word = line[1]
    transgressive = transgressives(word)
    transgressives_list.append(transgressive)
    print(line[1], ' -- ', transgressive)

print(transgressives_list)
input_len = len(input("\nВведіть що завгодно, якщо хочете додати список дієприслівників до окремого файлу, або просто натисніть Enter, щоб закрити програму :) "))
if input_len != 0:
    with open("output.txt", "a", encoding="windows-1251") as file:
        file.write(str(transgressives_list))
