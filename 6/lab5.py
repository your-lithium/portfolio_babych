print("Бабич Вероніка, ПЛ-3, 1 підгрупа, ЛР№5")

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk import sent_tokenize
from nltk.corpus import wordnet as wn


def freq_table(text_string) -> dict:
    stopWords = set(stopwords.words("english"))
    words = word_tokenize(text_string)
    ps = PorterStemmer()
    freqTable = dict()
    for word in words:
        word = ps.stem(word)
        if word in stopWords:
            continue
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1
    return freqTable


def score_sentences(sentences, freqTable) -> dict:
    sent_value = dict()
    for sent in sentences:
        word_count_in_sentence = (len(word_tokenize(sent)))
        for wordValue in freqTable:
            if wordValue in sent.lower():
                if sent[:15] in sent_value:
                    sent_value[sent[:15]] += freqTable[wordValue]
                else:
                    sent_value[sent[:15]] = freqTable[wordValue]
        sent_value[sent[:15]] = sent_value[sent[:15]] / word_count_in_sentence
    return sent_value


def avg_score(sentValue) -> float:
    sumValues = 0
    for entry in sentValue:
        sumValues += sentValue[entry]
        average = sumValues / len(sentValue)
    return average


def summary(sentences, sentValue, threshold):
    sentence_count = 0
    summary = ''
    for sent in sentences:
        if sent[:15] in sentValue and sentValue[sent[:15]] > (threshold):
            summary += " " + sent
            sentence_count += 1
    return summary


with open("catstory.txt", "r", encoding="utf-8") as catstory:
    cat_text = catstory.read()

ft = freq_table(cat_text)
s = sent_tokenize(cat_text)
sv = score_sentences(s, ft)
# avg = avg_score(sv)
avg = 1
summ = summary(s, sv, avg)
print("\nSummary #1:")
print(summ)

avg = 0.65
summ = summary(s, sv, avg)
print("\nSummary #2:")
print(summ)

print("\niron-1 entailments:")
print(wn.synset('iron.v.01').entailments())


def rte_features(rtepair):
    extractor = nltk.RTEFeatureExtractor(rtepair)
    features = {}
    features['word_overlap'] = len(extractor.overlap('word'))
    features['word_hyp_extra'] = len(extractor.hyp_extra('word'))
    features['ne_overlap'] = len(extractor.overlap('ne'))
    features['ne_hyp_extra'] = len(extractor.hyp_extra('ne'))
    return features


rtepair = nltk.corpus.rte.pairs(['rte3_dev.xml'])[0]
extractor = nltk.RTEFeatureExtractor(rtepair)

print("\nКлючові слова з тексту:")
print(extractor.text_words)
print("Ключові слова з гіпотези:")
print(extractor.hyp_words)
print("Перекриття між текстом і гіпотезою серед звичайних слів:")
print(extractor.overlap('word'))
print("Перекриття між текстом і гіпотезою серед іменованих сутностей (NE):")
print(extractor.overlap('ne'))
print("Звичайні слова, які містяться лише в гіпотезі:")
print(extractor.hyp_extra('word'))
print("Іменовані сутності, які містяться лише в гіпотезі:")
print(extractor.hyp_extra('ne'))
