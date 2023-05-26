print("Бабич Вероніка, 2 підгрупа, ЛР№4")

import nltk
# nltk.download('movie_reviews')
from nltk.corpus import movie_reviews
import random
import pickle
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.svm import SVC

doc = [(list(movie_reviews.words(fileid)), category) for category in movie_reviews.categories()
       for fileid in movie_reviews.fileids(category)]
random.shuffle(doc)

all_words = []
for w in movie_reviews.words():
    all_words.append(w.lower())
all_words = nltk.FreqDist(all_words)
print("\nThe most common 20 words are:")
print(all_words.most_common(20))

print("\nThe frequency for word \"awesome\" in all reviews is " + str(all_words["awesome"]) +".")

pos_words = []
neg_words = []
for f in doc:
    if f[1] == "neg":
        for w in f[0]:
            neg_words.append(w.lower())
    else:
        for w in f[0]:
            pos_words.append(w.lower())
pos_words = nltk.FreqDist(pos_words)
neg_words = nltk.FreqDist(neg_words)
print("\nThe frequency for word \"awesome\" in positive reviews is " + str(pos_words["awesome"]) +".")
print("The frequency for word \"awesome\" in negative reviews is " + str(neg_words["awesome"]) +".")

word_features = list(all_words.keys())[:2400]
def find_features(d):
    words = set(d)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features

found_words = []
for k, v in find_features(movie_reviews.words('pos/cv000_29590.txt')).items():
    if v is True:
        found_words.append(k)
print("\nThe most frequent 2400 words that are in this file are:")
print(found_words)

featuresets = [(find_features(rev), category) for(rev, category) in doc]
training_set = featuresets[:1800]
testing_set = featuresets[1800:]
# classifier = nltk.NaiveBayesClassifier.train(training_set)
# save_classifier = open("naivebayes.pickle", "wb")
# pickle.dump(classifier, save_classifier)
# save_classifier.close()
classifier_f = open("naivebayes.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()

print("\nNaive Bayes Algorithm accuracy percent:", (nltk.classify.accuracy(classifier, testing_set))*100)

print()
classifier.show_most_informative_features(20)

svc_classifier = SklearnClassifier(SVC(), sparse=False).train(training_set)
save_classifier = open("svc.pickle", "wb")
pickle.dump(classifier, save_classifier)
save_classifier.close()
# classifier_fs = open("svc.pickle", "rb")
# svc_classifier = pickle.load(classifier_fs)
# classifier_fs.close()

print("\nSVC Algorithm accuracy percent:", (nltk.classify.accuracy(svc_classifier, testing_set))*100)
