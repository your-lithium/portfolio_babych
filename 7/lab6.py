from telethon.sync import TelegramClient
from termcolor import colored
import re
import pytz

zone = "Europe/Kiev"
#  mission failed respect- за Kiev
local_tz = pytz.timezone(zone)

print("Бабич Вероніка, ПЛ-3, 1 підгрупа, ЛР№5\n")

api_id = 00000000
api_hash = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
username = "your_lithium"


with TelegramClient(username, api_id, api_hash) as client:
    client.start()

    channel_name = "gpt3cats"
    channel_entity = client.get_entity(channel_name)
    ch_date = channel_entity.date.replace(tzinfo=pytz.utc).astimezone(local_tz)
    print("ID каналу: {}\nusername каналу: {}\nНазва каналу: {}\nДата створення каналу: {}\n".format(
        channel_entity.id, channel_entity.username, channel_entity.title, ch_date))

    msgs = client.iter_messages(channel_entity, limit=5)
    for i, msg in enumerate(msgs):
        print(colored("Пост #{}:".format(i+1), "green"))
        words = [word for word in msg.text.split() if re.search("[a-zA-Z]", word)]
        msg_date = msg.date.replace(tzinfo=pytz.utc).astimezone(local_tz)
        print("Дата й час публікації: {}\nЗміст:\n{}\nКількість знаків: {}\nКількість слів: {}\n".format(msg_date, msg.text, len(msg.text), len(words)))

    msgs = client.iter_messages(channel_entity, reverse=True)
    with open("gpt3cats.txt", "w") as file:
        for msg in msgs:
            try:
                msg_date = msg.date.replace(tzinfo=pytz.utc).astimezone(local_tz)
                file.write(str(msg_date))
                file.write("\n")
                file.write(msg.text)
                file.write("\n\n\n\n")
            except TypeError:
                continue

    tpolph_name = "tpolph3_2021"
    tpolph_entity = client.get_entity(tpolph_name)
    msg_count = 0
    for msg in client.iter_messages(tpolph_entity):
        msg_count += 1
    print("Кількість постів на каналі ТПОЛПГ: " + str(msg_count))
