# імпортування потрібних бібліотек
import re
import sqlite3
import stanza
# stanza.download("uk")
import tkinter as tk
import matplotlib.pyplot as plt
from termcolor import colored

from os import listdir
from tkinter import ttk
from tkinter.filedialog import askdirectory
from math import sqrt

# визначення списку частиномовних тегів, властивих бібліотеці stanza, і приписування їм назв
POS_TAGS = {
    'NOUN': 'Іменник',
    'ADJ': 'Прикметник',
    'NUM': 'Числівник',
    'PRON': 'Займенник',
    'DET': 'Займенник',
    'VERB': 'Дієслово',
    'AUX': 'Дієслово "бути"',
    'ADV': 'Прислівник',
    'SCONJ': 'Сполучник підрядності',
    'CCONJ': 'Сполучник сурядності',
    'ADP': 'Прийменник',
    'PART': 'Частка',
    'INTJ': 'Вигук',
    'PROPN': 'Власна назва',
    'NONE': 'Без частини мови'
}


class Word:
    # представлення словоформи, яка буде вводитися до таблиці слововживань

    # form - словоформа
    # lemma - лема
    # pos - part of speech, частина мови
    # sub_id - номер підвибірки, до якої входить словоформа
    # freq - частота словоформи у підвибірці sub_id

    def __init__(self, form, lemma, pos, sub_id, sub_freq):
        self.form = form
        self.lemma = lemma
        self.pos = POS_TAGS.get(pos, 'Без частини мови')
        self.sub_id = sub_id
        self.sub_freq = sub_freq

    @classmethod
    def from_str(cls, word_str, sub_id, sub_freq):
        # створення об'єкту класу Word з об'єкту stanza word_str

        return cls(word_str[0], word_str[1], word_str[2], sub_id, sub_freq)

    def to_tuple(self) -> tuple:
        # створення кортежу із необхідними для заповнення таблиці слововживань даними

        freqs = [0] * 20
        freqs[self.sub_id] = self.sub_freq
        freqs.append(self.sub_freq)

        return (self.form, self.lemma, self.pos, *freqs)


class Subsample:
    # представлення підвибірки із 1000 слів

    # text - цілий текст підвибірки (із відповідного файлу)
    # sub_id - номер підвибірки
    # tokens - список токенів даної підвибірки (включно з пунктуацією)
    # words - список слововживань підвибірки (вилучається зі списку tokens) у формі об'єктів stanza

    # __len__ - повертає кількість слововживань
    # get_lexemes - повертає список об'єктів Wordform для даної підвибірки

    def __init__(self, text, sub_id):
        self.text = text
        self.sub_id = sub_id
        print(colored("Subsample {} read.".format(self.sub_id + 1), "green"))
        sentences = [sentence.words for sentence in nlp(self.text).sentences]
        self.tokens = [token for sentence in sentences for token in sentence]
        print(colored("Subsample {} parsed.\n".format(self.sub_id + 1), "green"))
        self.word_strs = []
        for token in self.tokens:
            if token.pos not in ["PUNCT", "SYM"] and len(self.word_strs) < 1000:
                if token.pos in ["NUM", "ADJ"] and bool(re.search(r'\d', token.text)):
                    continue
                else:
                    self.word_strs.append((token.text, token.lemma, token.upos))
            elif len(self.word_strs) == 1000:
                break
        self._index = 0

    def __len__(self):
        return len(self.word_strs)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self.word_strs):
            raise StopIteration
        i = self._index
        self._index += 1
        return self.word_strs[i]

    def __getitem__(self, index):
        return self.word_strs[index]

    def get_words(self) -> list:
        # повернення списку об'єктів Word для даної підвибірки

        words_excl = set()
        words = []

        for word_str in self:
            if not word_str in words_excl:
                word = Word.from_str(word_str, self.sub_id,
                                     self.word_strs.count(word_str))
                words.append(word)
                words_excl.add(word_str)
        return words


class Sample:
    # представлення всієї вибірки для стилю та оперування таблицями

    # source - джерело вибірки (потрібно вказувати для правильної роботи SQL-запитів)
    # subsamples - список об'єктів Subsample, що входять до складу вибірки
    # sql - словник SQL-запитів відповідно до стилю вибірки

    # word_table - створення та наповнення таблиці словоформ вибірки
    # lem_table - створення та наповнення таблиці лем вибірки
    # pos_table - створення та наповнення таблиці частин мов вибірки

    def __init__(self, source, subsamples):
        self.source = source
        self.subsamples = subsamples
        self.sql = SQL(source)
        self._index = 0

        self.create_tables()

    def __len__(self):
        return sum([len(sub) for sub in self])

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self.subsamples):
            raise StopIteration
        i = self._index
        self._index += 1
        return self.subsamples[i]

    def __getitem__(self, index):
        return self.subsamples[index]

    def create_tables(self) -> None:
        self.sql.word_freqs(self)
        self.sql.pos_freqs()

    def var_series(self) -> dict:
        # варіаційні ряди

        var_series_by_pos = {}

        for pos in POS_TAGS.values():
            var_series = {}
            self.sql.get_pos_freqs(pos)
            try:
                for freq in cur.fetchone():
                    var_series[freq] = var_series.get(freq, 0) + 1
            except TypeError:
                print("There was an error.")
            var_series_by_pos[pos] = var_series

        return var_series_by_pos

    def statistics(self) -> dict:
        # основні статистичні характеристики

        statistics = {}

        for pos in POS_TAGS.values():

            self.sql.get_pos_freqs(pos)
            freqs = cur.fetchone()
            pos_stats = (
                self._abs_freq(freqs),
                self._avg_freq(freqs),
                self._rel_freq(freqs),
                self._std_dev(freqs),
                self._conf_int_2_sgm(freqs),
                self._sigma_x(freqs),
                self._conf_int_2_sgm_x(freqs),
                self._coef_of_var(freqs),
                self._max_coef_of_var(freqs),
                self._coef_of_stbl(freqs),
                self._rel_err(freqs)
            )
            statistics[pos] = pos_stats

        return statistics

    @staticmethod
    def _abs_freq(freqs: tuple) -> int:
        # абсолютна частота частини мови у вибірці
        try:
            return sum(freqs)
        except (TypeError, ZeroDivisionError):
            return 0

    @staticmethod
    def _avg_freq(freqs: tuple) -> float:
        # середня частота частини мови у вибірці
        try:
            return round(sum(freqs) / len(freqs), 2)
        except (TypeError, ZeroDivisionError):
            return 0

    def _rel_freq(self, freqs: tuple) -> float:
        # відносна частота частини мови у вибірці
        try:
            return round(sum(freqs) / len(self), 3)
        except (TypeError, ZeroDivisionError):
            return 0

    def _std_dev(self, freqs: tuple) -> float:
        # середньоквадратичне відхилення частини мови у вибірці

        avg_freq = self._avg_freq(freqs)
        try:
            return round(
                         sqrt(sum([(freq - avg_freq) ** 2 for freq in freqs]) / len(freqs)),
                         ndigits=2
                         )
        except (TypeError, ZeroDivisionError):
            return 0

    def _conf_int_2_sgm(self, freqs: tuple) -> str:
        # довірчий інтервал 2σ частини мови у вибірці

        low = round(self._avg_freq(freqs) - (self._std_dev(freqs) * 2), 2)
        upp = round(self._avg_freq(freqs) + (self._std_dev(freqs) * 2), 2)

        try:
            return f"{low}-{upp}"
        except (TypeError, ZeroDivisionError):
            return 0

    def _sigma_x(self, freqs: tuple) -> float:
        # міра коливання середньої частоти частини мови у вибірці
        try:
            return round(self._std_dev(freqs) / sqrt(len(freqs)), 2)
        except (TypeError, ZeroDivisionError):
            return 0

    def _conf_int_2_sgm_x(self, freqs: tuple) -> str:
        # довірчий інтервал 2σх̅ частини мови у вибірці

        low = round(self._avg_freq(freqs) - (self._sigma_x(freqs) * 2), 2)
        upp = round(self._avg_freq(freqs) + (self._sigma_x(freqs) * 2), 2)

        try:
            return f"{low}-{upp}"
        except (TypeError, ZeroDivisionError):
            return 0

    def _coef_of_var(self, freqs: tuple) -> float:
        # коефіцієнт варіації частини мови у вибірці
        try:
            return round(self._std_dev(freqs) / self._avg_freq(freqs), 2)
        except (TypeError, ZeroDivisionError):
            return 0

    def _max_coef_of_var(self, freqs: tuple) -> float:
        # максимальний коефіцієнт варіації частини мови у вибірці
        try:
            return round(sqrt(len(freqs) - 1), 2)
        except (TypeError, ZeroDivisionError):
            return 0

    def _coef_of_stbl(self, freqs: tuple) -> float:
        # коефіцієнт стабільності частини мови у вибірці

        coef_of_var = self._coef_of_var(freqs)
        max_coef_of_var = self._max_coef_of_var(freqs)

        try:
            return round(1 - (coef_of_var / max_coef_of_var), 2)
        except (TypeError, ZeroDivisionError):
            return 0

    def _rel_err(self, freqs: tuple) -> float:
        # відносна похибка дослідження

        avg_freq = self._avg_freq(freqs)
        sigma_x = self._sigma_x(freqs)

        try:
            return round(1.96 * sigma_x / avg_freq, 2)
        except (TypeError, ZeroDivisionError):
            return 0


class SQL:
    # клас SQL-запитів та методів створення частотних таблиць вибірки

    def __init__(self, source: str) -> None:
        self.create_word_freqs = f'''CREATE TABLE word_freqs_{source} (
                                     word TEXT NOT NULL,
                                     lemma TEXT DEFAULT '—',
                                     pos TEXT DEFAULT '—',
                                     freq_01 INTEGER DEFAULT 0,
                                     freq_02 INTEGER DEFAULT 0,
                                     freq_03 INTEGER DEFAULT 0,
                                     freq_04 INTEGER DEFAULT 0,
                                     freq_05 INTEGER DEFAULT 0,
                                     freq_06 INTEGER DEFAULT 0,
                                     freq_07 INTEGER DEFAULT 0,
                                     freq_08 INTEGER DEFAULT 0,
                                     freq_09 INTEGER DEFAULT 0,
                                     freq_10 INTEGER DEFAULT 0,
                                     freq_11 INTEGER DEFAULT 0,
                                     freq_12 INTEGER DEFAULT 0,
                                     freq_13 INTEGER DEFAULT 0,
                                     freq_14 INTEGER DEFAULT 0,
                                     freq_15 INTEGER DEFAULT 0,
                                     freq_16 INTEGER DEFAULT 0,
                                     freq_17 INTEGER DEFAULT 0,
                                     freq_18 INTEGER DEFAULT 0,
                                     freq_19 INTEGER DEFAULT 0,
                                     freq_20 INTEGER DEFAULT 0,
                                     total INTEGER DEFAULT 0)
                                     '''
        self.insert_into_word_freqs = f'''INSERT INTO word_freqs_{source} VALUES (
                                          ?,?,?,?,?,?,?,?,?,?,?,?,
                                          ?,?,?,?,?,?,?,?,?,?,?,?)
                                          '''
        self.drop_word_freqs = f'DROP TABLE IF EXISTS word_freqs_{source}'
        self.create_pos_freqs = f'''CREATE TABLE pos_freqs_{source} AS
                                    SELECT pos,
                                    SUM(freq_01) AS freq_01,
                                    SUM(freq_02) AS freq_02,
                                    SUM(freq_03) AS freq_03,
                                    SUM(freq_04) AS freq_04,
                                    SUM(freq_05) AS freq_05,
                                    SUM(freq_06) AS freq_06,
                                    SUM(freq_07) AS freq_07,
                                    SUM(freq_08) AS freq_08,
                                    SUM(freq_09) AS freq_09,
                                    SUM(freq_10) AS freq_10,
                                    SUM(freq_11) AS freq_11,
                                    SUM(freq_12) AS freq_12,
                                    SUM(freq_13) AS freq_13,
                                    SUM(freq_14) AS freq_14,
                                    SUM(freq_15) AS freq_15,
                                    SUM(freq_16) AS freq_16,
                                    SUM(freq_17) AS freq_17,
                                    SUM(freq_18) AS freq_18,
                                    SUM(freq_19) AS freq_19,
                                    SUM(freq_20) AS freq_20,
                                    SUM(total) AS total
                                    FROM word_freqs_{source}
                                    GROUP BY pos
                                    ORDER BY SUM(total) DESC;
                                    '''
        self.drop_pos_freqs = f'DROP TABLE IF EXISTS pos_freqs_{source}'
        self.select_from_pos_freqs = f'''SELECT freq_01, freq_02, freq_03, freq_04,
                                         freq_05, freq_06, freq_07, freq_08,
                                         freq_09, freq_10, freq_11, freq_12,
                                         freq_13, freq_14, freq_15, freq_16,
                                         freq_17, freq_18, freq_19, freq_20
                                         from pos_freqs_{source}
                                         WHERE pos = ?'''

    def word_freqs(self, sample) -> None:
        # створення таблиці слововживань для даної вибірки та її наповнення

        cur.execute(self.drop_word_freqs)
        cur.execute(self.create_word_freqs)

        for sub in sample:
            for word in sub.get_words():
                cur.execute(self.insert_into_word_freqs, word.to_tuple())

        con.commit()

    def pos_freqs(self) -> None:
        # створення таблиці частин мови для даної вибірки та її наповнення

        cur.execute(self.drop_pos_freqs)
        cur.execute(self.create_pos_freqs)
        con.commit()

    def get_pos_freqs(self, pos: str) -> None:
        # вилучення частот для конкретних частин мови

        cur.execute(self.select_from_pos_freqs, (pos,))


# усі подальші класи необхідні для побудови віконного інтерфейсу відображення інформації
class InputFrame(ttk.Labelframe):
    DESC = "Оберіть папку з текстами підвибірок та мовний стиль вибірки"
    SOURCES = ['nv', 'hromadske']

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.path = None
        self.name = None

        self.ent_dir = ttk.Entry(self, width=30, state='normal')
        self.btn_sel_dir = ttk.Button(self, text="...", width=4,
                                      command=self.sel_sample_dir)
        self.lbl_style = tk.Label(self, text="Джерело")

        self.combo_style_var = tk.StringVar(self)
        self.combo_style = ttk.Combobox(
            self,
            state='readonly',
            textvariable=self.combo_style_var,
            values=[
                "НВ",
                "Громадське"
            ]
        )

        self.btn_calculate = ttk.Button(self, text="Обрахувати", width=12,
                                        command=self.calculate)

        self._layout()

    def _layout(self) -> None:
        self.ent_dir.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.btn_sel_dir.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.combo_style.grid(row=2, column=0, sticky='w', padx=5)
        self.lbl_style.grid(row=2, column=1, sticky='w', padx=5)
        self.btn_calculate.grid(row=3, column=1, sticky='e', padx=5, pady=5)

    def sel_sample_dir(self) -> None:
        self.path = askdirectory(title="Оберіть папку")
        self.name = re.search(r'[^/]+$', self.path).group()
        self.ent_dir.delete(0, tk.END)
        self.ent_dir.insert(0, self.name)

    def calculate(self) -> None:
        subsamples = self._subsamples()
        style = self.SOURCES[self.combo_style['values'].index(self.combo_style.get())]
        self.master.sample = Sample(style, subsamples)

        statistics = self.master.sample.statistics()
        for pos in statistics:
            self.master.stats_frame.tree_stats.insert('', 'end', text=pos,
                                                      values=statistics[pos])

    def _subsamples(self) -> list:
        subsamples = []

        for i, f_name in enumerate(listdir(self.path)):
            with open(f'{self.path}\\{f_name}', encoding='windows-1251') as f:
                subsamples.append(Subsample(f.read(), i))

        return subsamples

    def _var_series(self):
        var_series_by_pos = {}

        for pos in POS_TAGS.values():
            var_series = {}
            self.sample.sql.get_pos_freqs(pos)
            for freq in cur.fetchone():
                var_series[freq] = var_series.get(freq, 0) + 1
            var_series_by_pos[pos] = var_series


class LegendFrame(ttk.Labelframe):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.lbl_abs_freq = tk.Label(self, text="x — абсолюна частота")
        self.lbl_avg_freq = tk.Label(self, text="x̄ — середня частота")
        self.lbl_rel_freq = tk.Label(self, text="p — відносна частота")
        self.lbl_std_dev = tk.Label(self, text="σ — середньоквадратичне відхилення")
        self.lbl_conf_int_2_sgm = tk.Label(self, text="x̄±2σ — довірчий інтервал 2σ")
        self.lbl_sigma_x = tk.Label(self, text="σx̄ — міра коливання середньої частоти")
        self.lbl_conf_int_2_sgm_x = tk.Label(self, text="x̄±2σx̄ — довірчий інтервал 2σx̄")
        self.lbl_coef_of_var = tk.Label(self, text="v — коефіцієнт варіації")
        self.lbl_max_coef_of_var = tk.Label(self, text="vmax — максимальний коефіцієнт варіації")
        self.lbl_coef_of_stbl = tk.Label(self, text="D — коефіцієнт стабільності")
        self.lbl_rel_err = tk.Label(self, text="ε — відносна похибка дослідження")

        self.lbl_abs_freq.grid(row=0, column=0, sticky='w')
        self.lbl_avg_freq.grid(row=1, column=0, sticky='w')
        self.lbl_rel_freq.grid(row=2, column=0, sticky='w')
        self.lbl_std_dev.grid(row=3, column=0, sticky='w')
        self.lbl_conf_int_2_sgm.grid(row=4, column=0, sticky='w')
        self.lbl_sigma_x.grid(row=5, column=0, sticky='w')
        self.lbl_conf_int_2_sgm_x.grid(row=6, column=0, sticky='w')
        self.lbl_coef_of_var.grid(row=7, column=0, sticky='w')
        self.lbl_max_coef_of_var.grid(row=8, column=0, sticky='w')
        self.lbl_coef_of_stbl.grid(row=9, column=0, sticky='w')
        self.lbl_rel_err.grid(row=10, column=0, sticky='w')


class VarSeriesFrame(ttk.Labelframe):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.lbl_pos = tk.Label(self, text="Частина мови:")

        self.combo_pos_var = tk.StringVar(self)
        self.combo_pos = ttk.Combobox(self, state='readonly', width=17,
                                      textvariable=self.combo_pos_var,
                                      values=list(POS_TAGS.values()))
        self.combo_pos.bind('<<ComboboxSelected>>', self.sel_pos)

        self.tree_var_series = ttk.Treeview(self, columns=('freq_var', 'sub_num'))
        self.tree_var_series.heading('freq_var', text="Частота")
        self.tree_var_series.heading('sub_num', text="Підвибірок")
        self.tree_var_series.column('#0', width=0)
        self.tree_var_series.column('freq_var', width=106)
        self.tree_var_series.column('sub_num', width=106)

        self.btn_plot = ttk.Button(self, text="Полігон частот", width=15,
                                   command=self.make_plot)

        self.lbl_pos.grid(row=0, column=0, sticky='e', padx=2, pady=5)
        self.combo_pos.grid(row=0, column=1, sticky='w', padx=2, pady=5)
        self.tree_var_series.grid(row=1, column=0, columnspan=2, pady=5)
        self.btn_plot.grid(row=2, column=1, sticky='e', pady=5)

    def sel_pos(self, *args) -> None:
        self.tree_var_series.delete(*self.tree_var_series.get_children())
        sel_pos = self.combo_pos.get()
        var_series = sorted(self.master.sample.var_series()[sel_pos].items())

        for i, pair in enumerate(var_series, start=1):
            self.tree_var_series.insert('', 'end', values=pair)

    def make_plot(self, *args):
        sel_pos = self.combo_pos.get()
        var_series = sorted(self.master.sample.var_series()[sel_pos].items())
        freqs = [pair[0] for pair in var_series]
        sub_nums = [pair[1] for pair in var_series]

        plt.plot(freqs, sub_nums)
        plt.title(f"Полігон частот: {sel_pos.lower()}")
        plt.xlabel("Варіанти абсолютної частоти")
        plt.ylabel("Кільскість підвибірок")
        plt.show()


class StatsFrame(ttk.Labelframe):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.tree_stats = ttk.Treeview(
            self, height=12,
            columns=('abs_freq', 'avg_freq', 'rel_freq', 'std_dev',
                     'conf_int_2_sgm', 'sigma_x', 'conf_int_2_sgm_x',
                     'coef_of_var', 'max_coef_of_var', 'coef_of_stbl', 'rel_err')
        )
        self.tree_stats.heading('abs_freq', text="x")
        self.tree_stats.heading('avg_freq', text="x̄")
        self.tree_stats.heading('rel_freq', text="p")
        self.tree_stats.heading('std_dev', text="σ")
        self.tree_stats.heading('conf_int_2_sgm', text="x̄±2σ")
        self.tree_stats.heading('sigma_x', text="σx̄")
        self.tree_stats.heading('conf_int_2_sgm_x', text="x̄±2σx̄")
        self.tree_stats.heading('coef_of_var', text="v")
        self.tree_stats.heading('max_coef_of_var', text="vmax")
        self.tree_stats.heading('coef_of_stbl', text="D")
        self.tree_stats.heading('rel_err', text="ε")

        self.tree_stats.column('#0', width=130)
        self.tree_stats.column('abs_freq', width=50)
        self.tree_stats.column('avg_freq', width=50)
        self.tree_stats.column('rel_freq', width=50)
        self.tree_stats.column('std_dev', width=50)
        self.tree_stats.column('conf_int_2_sgm', width=100)
        self.tree_stats.column('sigma_x', width=50)
        self.tree_stats.column('conf_int_2_sgm_x', width=100)
        self.tree_stats.column('coef_of_var', width=50)
        self.tree_stats.column('max_coef_of_var', width=50)
        self.tree_stats.column('coef_of_stbl', width=50)
        self.tree_stats.column('rel_err', width=50)

        self.tree_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                         command=self.tree_stats.xview)
        self.tree_stats['xscrollcommand'] = self.tree_scroll.set

        self.tree_stats.pack()
        self.tree_scroll.pack(fill=tk.X)


class SampleFrame(ttk.Labelframe):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.sample = None

        self.input_frame = InputFrame(self, text="Вхідні тексти", padding=5)
        self.legend_frame = LegendFrame(self, text="Легенда", padding=5)
        self.var_series_frame = VarSeriesFrame(self, text="Варіаційний ряд",
                                               padding=8)
        self.stats_frame = StatsFrame(self, text="Статистичні характеристики",
                                      padding=10)

        self.input_frame.grid(row=0, column=0, sticky='nw', padx=6)
        self.legend_frame.grid(row=1, column=0, sticky='we', padx=6)
        self.var_series_frame.grid(row=0, column=1, rowspan=2, sticky='ns', padx=6)
        self.stats_frame.grid(row=0, column=2, rowspan=2, sticky='ns', padx=6)


class Body(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.sample_frame_1 = SampleFrame(self, text="Вибірка 1", padding=10)
        self.sample_frame_2 = SampleFrame(self, text="Вибірка 2", padding=10)

        self.sample_frame_1.pack(pady=10)
        self.sample_frame_2.pack(pady=10)


class Application(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title("Статистичні характеристики вибірок")
        self.body = Body(self, padx=15, pady=15)
        # self.maxsize(1920, 1080)
        self.body.pack()


# запуск програми, ініціалізація NLP-пайплайну stanza
if __name__ == '__main__':

    con = sqlite3.connect('../frequencies.db')
    cur = con.cursor()
    nlp = stanza.Pipeline("uk")
    app = Application()
    app.mainloop()
    con.close()
