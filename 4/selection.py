import sqlite3

conn = sqlite3.connect("ukr_lexicon.db")
c = conn.cursor()

inp = input("Введіть абревіатуру словника, слова з якого ви хочете отримати.\n")
sel_inp = "SELECT Words FROM ukr_lexicon WHERE Dictionaries LIKE '" + inp + "' OR Dictionaries LIKE '% " + inp +\
          "' OR Dictionaries LIKE '" + inp + " %' OR Dictionaries LIKE '% " + inp + " %'"

words_list = []
for i in c.execute(sel_inp):
    words_list.append(i[0])

print(words_list)

conn.close()
