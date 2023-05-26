import sqlite3
import re

letter = "A"
case = "sgN"
new_word = "pies"
gender = 1
print("Бабич Вероніка, ПЛ-3, 1 підгрупа, ЛР№5\n")

conn = sqlite3.connect('pol_lab07.s3db')
cur = conn.cursor()

print("Перевірка з'єднання:")
cur.execute("SELECT sgN FROM tnoun WHERE sgN='dusza'")
print(cur.fetchone()[0])

print("\nВсі слова на літеру \"А\" у відмінку \"sgN\":")
cur.execute("SELECT sgN FROM tnoun WHERE sgN LIKE 'a_%'")
print(", ".join([str(word[0]) for word in cur.fetchall()]))

cur.execute(f"INSERT INTO tnoun (gender, sgN) VALUES(\'{gender}\', \'{new_word}\')")
cur.execute("SELECT sgN, gender FROM tnoun ORDER BY id DESC LIMIT 1")
print("\nДодано рядок:")
print(cur.fetchone())


def parse(lemma):
    pattern1 = re.compile(f"(?P<word>\w*)\t{lemma}\t(?P<tags>.+)")
    pattern2 = re.compile("(?<=sg:)[\w\.]+(?=:)")
    with open("parse_lab07.txt", "r", encoding="utf-8") as h:
        lines = h.readlines()

    valid = []
    for line in lines:
        check = re.match(pattern1, line)
        if check:
            valid.append(check.group("word", "tags"))

    for line in valid:
        iter = re.finditer(pattern2, line[1])
        if iter:
            for i in iter:
                if i.group(0) == "nom":
                    sgN = line[0]
                elif i.group(0) == "gen":
                    sgG = line[0]
                elif i.group(0) == "dat":
                    sgD = line[0]
                elif i.group(0) == "acc":
                    sgA = line[0]
                elif i.group(0) == "inst":
                    sgI = line[0]
                elif i.group(0) == "loc":
                    sgL = line[0]
                elif i.group(0) == "voc":
                    sgV = line[0]

    return [sgN, sgG, sgD, sgA, sgI, sgL, sgV]


forms = parse(new_word)
column_list = ["N", "G", "D", "A", "I", "L", "V"]

for i, column in enumerate(column_list):
    cur.execute(f"UPDATE tnoun SET sg{column}=\'{forms[i]}\' WHERE sgN = \'{new_word}\'")
cur.execute(f"SELECT * FROM tnoun ORDER BY id DESC LIMIT 1")
print("\nОновлено рядок:")
print(cur.fetchone())
conn.commit()
