import re


def transgressives(verb, v_aspect, conjugation):
    sya_bool = False
    if re.fullmatch("[\w']+ся", verb) is not None:
        sya_bool = True
        verb = verb[:-2]

    if re.fullmatch("[\w']+[ую]вати", verb) is not None and v_aspect != "D":
        verb = verb[:-4]
    else:
        verb = verb[:-2]

    if v_aspect == "N":
        if conjugation == "1":
            if re.fullmatch("[\w']+ч", verb) is not None:
                transgressive = verb + "учи"
            elif re.fullmatch("[\w']+ч[иі]", verb) is not None:
                transgressive = verb[:-1] + "учи"
            elif re.fullmatch("[\w']+[ауое]я", verb) is not None:
                transgressive = verb[:-1] + "ючи"
            else:
                transgressive = verb + "ючи"
        else:
            if re.fullmatch("[\w']+[жчшщ][аи]", verb) is not None:
                transgressive = verb[:-1] + "ачи"
            elif re.fullmatch("[\w']+[мвбпф]и", verb) is not None:
                transgressive = verb[:-1] + "лячи"
            elif re.fullmatch("[\w']+[иі]", verb) is not None:
                transgressive = verb[:-1] + "ячи"
            else:
                transgressive = verb + "ячи"
    else:
        if re.fullmatch("[\w']+[аоуеиіяюєї]", verb) is not None:
            transgressive = verb + "вши"
        else:
            transgressive = verb + "ши"

    if sya_bool is True:
        transgressive += "ся"
    return transgressive


file_name = input("Вкажіть назву вашого файлу: ")
if len(file_name) < 1: file_name = "words.csv"
with open(file_name) as file:
    lines = file.readlines()

lines.pop(0)
transgressives_list = []
for line in lines:
    line = (line.strip(";\n")).split(";")
    word, w_aspect, w_conjugation = line[1], line[2], line[4]
    transgressive = transgressives(word, w_aspect, w_conjugation)
    transgressives_list.append(transgressive)
    print(line[1], ' -- ', transgressive)

print(transgressives_list)
input("\nНатисніть Enter, щоб закрити програму :)")
