import json
import re
from datetime import datetime as dt

import discord
from discord.ext import commands
from pwn import enhex
from random import choice

from configure import configure, birthday_dict, month_translate
from youtube_finder import youtube_finder

response_controller = [
    {
        "command": "hello",
        "key_words": r"(\bпривет\b)|(\bприв\b)|(\bдаров\b)|(\bку\b)",
    },
    {
        "command": "test",
        "key_words": r"(\bработаешь\b)|"
                     r"(\bвключена\b)|"
                     r"(\bтест\b)|"
                     r"(\bотвечаешь\b)|"
                     r"(\bкак дела\b)|"
                     r"(\bспишь\b)"
                     r"(\bты как\b)",
    },
    {
        "command": "birthday",
        "key_words": r"(\bдень рождения\b)|(\bдр\b)",
    },
    {
        "command": "say_hello",
        "key_words": r"(\bпоздоровайся\b)|"
                     r"(\bрасскажи о себе\b)|"
                     r"(\bчто ты\b)|"
                     r"(\bкто ты\b)",
    },
    {
        "command": "what_i_can",
        "key_words": r"(\bумеешь\b)",
    },
    {
        "command": "some_choice",
        "key_words": r"(\b или \b)",
    },
    {
        "command": "find_in_youtube",
        "key_words": r"(\bнайди видео\b)|"
                     r"(\bнайти видео\b)|"
                     r"(\bпокажи видео\b)",
    },
]

error_responses = [
    "Я не знаю что на это сказать. Простите!\nЯ еще только учусь. ",
    "К сожалению, я не имею ни малейшего понятия "
    "что отвечать на ваш вопрос. Простите!",
    "Ах если бы я знала и могла ответить на поставленную задачу...",
    "Знаете. Мир прекрасен. И огромен. И в нем куча НЕИЗВЕДАННОГО...",
    "Когда-нибудь я обязательно научусь отвечать на такого рода запросы...",
    "Я работаю за идею, а потому моё обучение проходит крайне медленно... "
    "Может быть, мы решим ваш вопрос завтра?..",
]


def log_response(message, response):
    response_log = {
        "response_time": [dt.today().strftime("%d-%m-%Y"),
                          dt.now().time().strftime("%H:%M:%S")],
        "to_author_id": message.author.id,
        "response_content": enhex(bytes(response, encoding="utf-8")),
        "channel_id": message.channel.id
    }
    with open(f"log_{dt.today().strftime('%d-%m-%Y')}.json",
              'a',
              encoding="utf-8") as log_dump:
        json.dump(response_log,
                  log_dump,
                  indent=4,
                  ensure_ascii=False)
        log_dump.write(",\n")
    print(response_log)


async def test(client: commands.Bot, message) -> bool:
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    response: str = "Вроде, всё должно работать. Если что - я пишу логи!"
    await channel.send(response)
    log_response(message, response)
    return True


async def hello(client: commands.Bot, message) -> bool:
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    author = message.author.name
    response: str = f"Привет, {author}! "
    await channel.send(response)
    log_response(message, response)
    return True


async def birthday(client: commands.Bot, message=None) -> bool:
    today = dt.today().strftime("%d-%m")
    month = dt.today().strftime("%B")
    if month in month_translate:
        month = month_translate[month]
    today_full = dt.today().strftime(f"%d {month} %Y")
    if today in birthday_dict:
        tag = birthday_dict[today]
        response: str = (f"Сегодня, {today_full},"
                         f"день рождения у {client.get_user(tag).mention}\n"
                         f"Поздравляю! Любви и радости желаю :)")
    else:
        response: str = f"Сегодня, {today_full}, ни у кого ДР нет :)"
    if message is not None:
        channel_id = message.channel.id
        channel = client.get_channel(channel_id)
    else:
        channel = client.get_channel(381930105242386435)
    await channel.send(response)
    log_response(message, response)
    return True


async def say_hello(client: commands.Bot, message) -> bool:
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    response: str = ("Доброго всем времени суток!\n"
                     "Я - Мементо. Начинающий бот-помощник для"
                     f"{client.get_user(276397179982315520).mention}.\n"
                     "Пока я умею совсем немного, но, думаю,"
                     "что меня научат :)")
    await channel.send(response)
    log_response(message, response)
    return True


async def what_i_can(client: commands.Bot, message) -> bool:
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    response: str = ("Я умею сильно мало!\n"
                     "Пока я могу сказать только когда у кого День Рождения из"
                     " ограниченного круга известных мне лиц.\n"
                     "Также я могу искать видео в YouTube!\n"
                     "Думаю, попозже, меня научат еще чему-нибудь. "
                     "Я надеюсь...")
    await channel.send(response)
    log_response(message, response)
    return True


async def find_in_youtube(client: commands.Bot, message) -> bool:
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    content = message.content.lower()
    query: str = content.replace("мементо", "")
    try:
        query = query.split("найди видео")[1]
    except IndexError:
        pass
    try:
        query = query.split("покажи видео")[1]
    except IndexError:
        pass
    try:
        query = query.split("найти видео")[1]
    except IndexError:
        pass
    query = query.replace(" ", "+")
    link = youtube_finder(query)
    response = ("Я смогла найти вот такое видео по запросу "
                f"`{query.replace('+', ' ')}`: {link} \n"
                "В дальнейшем я смогу его скачать и залить сюда."
                " Пока не могу.")
    await channel.send(response)
    log_response(message, response)
    return True


async def some_choice(client: commands.Bot,
                      message) -> bool:
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    content = (message.content).lower()
    choices: str = content.replace("мементо", "")
    bad_chars = [",", ".", "-", "!", "?"]
    dub = client.get_user(276397179982315520).mention
    for item in bad_chars:
        if item in choices:
            choices = choices.replace(item, "")
    choices = choices.split("или")
    for item in choices:
        if " " in item:
            item = item.replace(" ", "")
    response: str = ("Как искусственный интеллект "
                     "(на начальном этапе своего проектирования."
                     " Я еще не подключена к нейронным сетям),"
                     " я не могу иметь субъективных предпочтений или чувств,"
                     "поэтому не могу выбирать между "
                     f"`{choices[0]}` и `{choices[1]}`."
                     " Я способна только передавать информацию и "
                     "давать рекомендации на основе"
                     " анализа данных и логических выводов.\n"
                     "В любом случае, выбор персонажей или еды зависит от "
                     "личных предпочтений и"
                     " вкусов каждого человека, и каждый может выбрать того "
                     "или то, кто или что ему больше нравится.\n"
                     "Дополнительно лишь могу сказать, что, так как я "
                     "являюсь лишь помощником,"
                     " в меня занесли некоторые критерии выбора. То есть:\n"
                     f" - Я думаю, что {dub} выбрал бы Трисс;\n"
                     f" - Я думаю, что {dub} пельмени не очень любит;\n"
                     f" - Я думаю, что {dub} сказал бы: "
                     "`Изначальному автору произведения лучше знать кого "
                     "выбирать главному герою`.\n"
                     "Еще у меня есть большой брат, в который интегрирован "
                     "GPT-3.5: `https://poe.com/AnswererBOT`.\n"
                     "Можно у него что-нибудь спросить!\n")
    await channel.send(response)
    log_response(message, response)
    return True

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix=configure["prefix"],
                      intents=intents)


@client.event
async def on_ready():
    # channel = client.get_channel(381930105242386435)
    # await channel.send("Я пробудилась ото сна.")
    start_log_response = {
        "start_time": [dt.today().strftime("%d-%m-%Y"),
                       dt.now().time().strftime("%H:%M:%S")],
        "channel_info": client.get_channel(381930105242386435),
        "users_info": client.users,
    }
    print(start_log_response)


@client.event
async def on_message(message):
    author = message.author.name
    content = (message.content).lower()
    channel_id = message.channel.id
    log: dict = {
        "time": [dt.today().strftime("%d-%m-%Y"),
                 dt.now().time().strftime("%H:%M:%S")],
        "author": str(message.author),
        "content": enhex(bytes(str(content).replace("\n", " "),
                               encoding="utf-8")),
        "channel_id": channel_id
    }
    for prefix in configure["prefix"]:
        if prefix in content and author != "Memento":
            with open(f"log_{dt.today().strftime('%d-%m-%Y')}.json",
                      'a',
                      encoding="utf-8") as log_dump:
                json.dump(log,
                          log_dump,
                          indent=4,
                          ensure_ascii=False)
                log_dump.write(",\n")
            print(log)
            response_for_send: str = ""
            response_answer: bool = False
            for item in response_controller:
                if re.search(item["key_words"], content) is not None:
                    if item["command"] == "hello":
                        response_answer = await hello(client, message)
                    elif item["command"] == "test":
                        response_answer = await test(client, message)
                    elif item["command"] == "birthday":
                        response_answer = await birthday(client, message)
                    elif item["command"] == "say_hello":
                        response_answer = await say_hello(client, message)
                    elif item["command"] == "what_i_can":
                        response_answer = await what_i_can(client, message)
                    elif item["command"] == "find_in_youtube":
                        response_answer = await find_in_youtube(client,
                                                                message)
                    elif item["command"] == "some_choice":
                        response_answer = await some_choice(client, message)
            if response_answer is False:
                response_for_send = choice(error_responses)
                channel = client.get_channel(channel_id)
                await channel.send(response_for_send)
                log_response(message, response_for_send)

client.run(configure["discord_token"])
