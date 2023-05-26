print("Бабич Вероніка, 2 підгрупа, ЛР№3")

import time
time.clock = time.time
import nltk
# nltk.download()
import chatterbot
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import chatterbot_corpus
import logging
from chatterbot.trainers import ChatterBotCorpusTrainer

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

# my_bot = ChatBot(name="PyBot", read_only=True, logic_adapters=["chatterbot.logic.MathematicalEvaluation",
#                                                                "chatterbot.logic.BestMatch"])
#
# small_talk = ["Hi there!", "Hi", "Hello", "How do you do?", "How are you?", "I'm cool", "Fine, and you?", "Always cool",
#               "I'm OK", "Glad to hear that", "I feel awesome", "Excellent, glad to hear that", "Not so good",
#               "Sorry to hear that", "What's your name?", "I'm PyBot. Ask me a math question, please"]
#
# math_talk_1 = ["pythagorean theorem", "a^2 + b^2 =  c^2"]
# math_talk_2 = ["law of cosines", "c^2 = a^2 + b^2 - 2*a*b*cos(gamma)"]
#
# list_trainer = ListTrainer(my_bot)
# for i in (small_talk, math_talk_1, math_talk_2):
#     list_trainer.train(i)
#
# print("Hi! Let's talk :з")
# for i in range(10):
#     user_input = input()
#     print(my_bot.get_response(user_input))


swedish_bot = ChatBot(name="PyBot", read_only=True, logic_adapters=["chatterbot.logic.MathematicalEvaluation",
                                                                    "chatterbot.logic.BestMatch"])
corpus_trainer = ChatterBotCorpusTrainer(swedish_bot)
corpus_trainer.train("chatterbot.corpus.swedish")

print("Hej!")
for i in range(15):
    user_input = input()
    print(swedish_bot.get_response(user_input))
