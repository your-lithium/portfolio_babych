print("Бабич Вероніка, 2 підгрупа, ЛР№2")

import numpy
import nltk
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import wordnet as wn
from nltk.metrics import edit_distance
from operator import itemgetter
from collections import Counter


class Word:
    def __init__(self, word):
        self.word = word

    def levenstein(self, compared: "Word"):
        return edit_distance(self.word, compared.word)

    def damerau_levenstein(self, compared: "Word"):
        return edit_distance(self.word, compared.word, transpositions=True)

    def closest_9(self):
        with open("1-1000.txt", "r") as stopwords_file:
            stopwords = stopwords_file.readlines()

        distances = {}
        for line in stopwords:
            line_word = Word(line.strip())
            word_distance = self.damerau_levenstein(line_word)
            distances[line.strip()] = word_distance
            sorted_dict = sorted(distances.items(), key=itemgetter(1))

        closest_words = []
        for i in range(9):
            closest_words.append(sorted_dict[i])

        print("\nThe closest 9 words for the word \"{}\" are:".format(self.word))
        for word, distance in closest_words:
            print("\"{}\" with the distance of {}.".format(word, distance))
        return closest_words

    def little_women(self):
        with open("alcott-women.txt", "r") as file:
            full_text = file.read()

        sent_text = sent_tokenize(full_text)
        word_text = []
        for sent in sent_text:
            word_text.extend([i.lower() for i in word_tokenize(sent) if i.isalnum()])
        count_text = Counter(word_text)

        words = []
        with open("alcott-women_counted.txt", "w") as file:
            for i in count_text.most_common():
                file.write(i[0] + "\n")
                words.append(i[0])

        distances = {}
        for line in words:
            line_word = Word(line.strip())
            word_distance = self.damerau_levenstein(line_word)
            distances[line.strip()] = word_distance
            sorted_dict = sorted(distances.items(), key=itemgetter(1))

        closest_words = []
        for i in range(9):
            closest_words.append(sorted_dict[i])

        print("\nThe closest 9 words for the word \"{}\" are:".format(self.word))
        for word, distance in closest_words:
            print("\"{}\" with the distance of {}.".format(word, distance))
        return closest_words


class Lexeme(Word):
    def __init__(self, word):
        super().__init__(word)
        self.synsets = [synset for synset in wn.synsets(word) if synset.pos() == "n"]
        self.synset = wn.synsets(word)[0]

    def definitions(self):
        for synset in self.synsets:
            print("\nThe definition for synset {}: {}".format(synset.name(), synset.definition()))

    def hypohyper(self):
        for synset in self.synsets:
            if synset.hyponyms():
                print("\nSynset {} has these hyponyms: {}.".format(synset.name(),
                                                                   [hyponym.name() for hyponym in synset.hyponyms()]))
            else:
                print("\nSynset {} has no hyponyms.".format(synset.name()))

            if synset.hypernyms():
                print("Synset {} has these hypernyms: {}.".format(synset.name(),
                                                                  [hypernym.name() for hypernym in synset.hypernyms()]))
            else:
                print("Synset {} has no hypernyms.".format(synset.name()))

    def lowest_common(self, compared: "Lexeme"):
        lc_synset = self.synset.lowest_common_hypernyms(compared.synset)
        print("\nThe lowest common hypernym for synsets {} and {} is {}.".format(self.synset.name(),
                                                                                   compared.synset.name(),
                                                                                   lc_synset[0].name()))
        return lc_synset

    def similarity(self, compared: "Lexeme"):
        path = self.synset.path_similarity(compared.synset)
        wupalmer = self.synset.wup_similarity(compared.synset)
        leacock_chodorow = self.synset.lch_similarity(compared.synset)
        print(
            "\nThe similarity of synsets {} and {} is as follows:\nPath: {}\nWu-Palmer: {}\nLeacock Chodorow: {}".format(
                self.synset.name(), compared.synset.name(), path, wupalmer, leacock_chodorow))
        return path, wupalmer, leacock_chodorow


lithium = Lexeme("lithium")
iron = Lexeme("iron")

lithium.definitions()
iron.definitions()
lithium.hypohyper()
iron.hypohyper()

lithium.lowest_common(iron)
iron.similarity(lithium)
lithium.levenstein(iron)
print("\nThe Levenstein distance between words {} and {} is {}.".format(lithium.word, iron.word,
                                                                        lithium.levenstein(iron)))
iron.damerau_levenstein(lithium)
print("\nThe Damerau-Levenstein distance between words {} and {} is {}.".format(lithium.word, iron.word,
                                                                                lithium.damerau_levenstein(iron)))

users = Word(input("\nВведіть довільне слово англійською. \n"))
users.closest_9()
users.little_women()
