import re
import sqlite3


def file_reader():
    with open("lexicon.md", "r", encoding="utf-8") as file:
        lexicon_file = file.read()
    return lexicon_file


def clean_and_split(file_text: str):
    file_lines = file_text.split("\n\n")

    entries = []
    for line in file_lines:
        if "\n" in line:
            entries.append(line.replace("\n", " "))
        else:
            entries.append(line)

    return entries


def divide(entries: list):
    parse_pattern = re.compile(r"^\*{2,3}(?P<name>.+)\*{2,3} (?:\[?\*(?P<gram_info>[^А-ЯІЇЄҐ]+)\*\[?)?(?P<dict_tuple>[\S\s]+?)$")
    divided_entries = []

    for i, entry in enumerate(entries):
        entry_match = re.fullmatch(parse_pattern, entry)
        if entry_match:
            name = entry_match.group("name")
            gram_info = entry_match.group("gram_info")
            dict_tuple = entry_match.group("dict_tuple").lstrip(" ")
            divided_entries.append([name, gram_info, dict_tuple, []])
        else:
            divided_entries[len(divided_entries)-1][3].append(entry)

    for i in divided_entries:
        if len(i[3]) == 0:
            i[3] = ""
        elif len(i[3]) == 1:
            i[3] = i[3][0]
        else:
            i[3] = "; ".join(i[3])

    return divided_entries


lexicon = (divide(clean_and_split(file_reader())))

print(len(lexicon))

conn = sqlite3.connect("ukr_lexicon.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS ukr_lexicon
             (id INTEGER PRIMARY KEY,
             words TEXT,
             grammatical_labels TEXT,
             dictionaries TEXT,
             additions TEXT)''')

for line in lexicon:
    c.executemany('''INSERT INTO ukr_lexicon(words, grammatical_labels, dictionaries, additions) VALUES(?, ?, ?, ?)''', (line,))

conn.commit()
for row in c.execute('SELECT * FROM ukr_lexicon'):
    print(row)

conn.close()
