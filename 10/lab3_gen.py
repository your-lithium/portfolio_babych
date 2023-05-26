print("Бабич Вероніка, 2 підгрупа, ЛР№3")

from collections import defaultdict
import random


class generator:
    def __init__(self, text):
        self.text = text
        self.markov = self.markov_chains()

    def markov_chains(self):
        words = self.text.split(" ")
        markov_dict = defaultdict(list)

        for current_word, next_word in zip(words[0:-1], words[1:]):
            markov_dict[current_word].append(next_word)
        markov_dict = dict(markov_dict)

        return markov_dict

    def generation(self, n: int):
        cur_word = random.choice(list(self.markov.keys()))
        gen_text = cur_word.capitalize()

        for i in range(n-1):
            next_word = random.choice(self.markov[cur_word])
            gen_text += " " + next_word
            cur_word = next_word

        gen_text += "."
        print(gen_text)


with open("alcott-women.txt", "r") as women:
    women_text = women.read()

women_generator = generator(women_text)
women_generator.generation(19)
