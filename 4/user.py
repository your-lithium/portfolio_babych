import sqlite3

conn = sqlite3.connect("ukr_lexicon.db")
c = conn.cursor()

inp = "open"
while inp != "закрити":
    inp = input("Введіть вашу команду для роботи з БД або введіть \"закрити\", щоб закрити програму.\n")
    try:
        for i in c.execute(inp):
            print(i)
        print()
    except:
        if inp != "закрити":
            print("На жаль, ваша команда містить помилку. Будь ласка, спробуйте ще раз.\n")

conn.close()
