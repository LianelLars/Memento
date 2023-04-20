import json
import re
from datetime import datetime as dt

import discord
from discord.ext import commands
from pwn import enhex
import requests as r

from configure import CONFIGURE, BIRTHDAY_DICT, MONTH_TRANSLATE
from youtube_finder import youtube_finder

RESPONSE_CONTROLLER: list[dict[str:str, str]] = [
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
                     r"(\bнайди\b)|"
                     r"(\bнайти видео\b)|"
                     r"(\bпокажи видео\b)",
    },
]

ERROR_RESPONSES: list[str] = [
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
    """
    Function for logs.
    """
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
    """
    Function for easy-query testing.
    """
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    response: str = "Вроде, всё должно работать. Если что - я пишу логи!"
    await channel.send(response)
    log_response(message, response)
    return True


async def hello(client: commands.Bot, message) -> bool:
    """
    Function for answer on 'Hello' message :)
    """
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    author = message.author.name
    response: str = f"Привет, {author}! "
    await channel.send(response)
    log_response(message, response)
    return True


async def birthday(client: commands.Bot, message=None) -> bool:
    """
    Function for `birthday` parsing. Dict u can find in `CONFIGURE`.\n
    #TODO:
      #Create list for random choise of congratilations\n
      #Create sub-function for parsing users.\n
      #Send response automaticaly to `major` channel.
    """
    today = dt.today().strftime("%d-%m")
    month = dt.today().strftime("%B")
    if month in MONTH_TRANSLATE:
        month = MONTH_TRANSLATE[month]
    today_full = dt.today().strftime(f"%d {month} %Y")
    if today in BIRTHDAY_DICT:
        tag = BIRTHDAY_DICT[today]
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
    """
    Function for saying first hello and small talk about this application.
    """
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
    """
    Function talking about "what Memento can do"
    """
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    response: str = ("Я умею уже сильно побольше!\n"
                     "Я могу напомнить у кого `сегодня` День Рождения из"
                     " ограниченного круга известных мне лиц.\n"
                     "Также я могу искать видео в YouTube и "
                     "отвечать на каверзные вопросы!\n"
                     "Думаю, попозже, меня научат еще чему-нибудь. "
                     "Хотя, в целом, я уже выполняю "
                     "возложенные на меня обязанности :)")
    await channel.send(response)
    log_response(message, response)
    return True


async def find_in_youtube(client: commands.Bot, message) -> bool:
    """
    Function for finding video in youtube by `message.author` query.\n
    // So, I'm from Russia. This thing is very hard to be friends with VPNs\n
    // Connect to `YouTube` host can be TOO long (around 2 min). Be patient :)
    """
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
    response = ("Я смогла найти вот такое видео: "
                f"{link} \n"
                "В дальнейшем я смогу его скачать и залить сюда."
                " Пока не могу.")
    await channel.send(response)
    log_response(message, response)
    return True


async def open_ai_integrate(client: commands.Bot, message) -> bool:
    """
    Function for calling `OpenAI` technology.\n
    // VPNs nessesary. Cause Russia.\n
    // If u have subscribe for `OpenAI` u can use your own api\n
    and u will not have some limit for request.
    //But i haven't enought money, so...
    """
    channel_id = message.channel.id
    channel = client.get_channel(channel_id)
    content: str = message.content.lower()[8:-1]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIGURE['open_ai_token']}",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/111.0.0.0 Safari/537.36",

    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.7
    }

    req = r.post(CONFIGURE["url_open_ai"], headers=headers, json=data)

    with open("open_ai.json", "w", encoding="utf-8") as json_dump:
        json_dump.write(req.text)
    with open('open_ai.json', encoding='utf-8') as req_file:
        response = json.load(req_file)
    response_for_send = response["choices"][0]["message"]["content"]
    await channel.send(response_for_send)
    log_response(message, response_for_send)
    return True


intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix=CONFIGURE["prefix"],
                      intents=intents)


@client.event
async def on_ready():
    """
    First time run function.
    """
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
    """
    Main Function
    """
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
    for prefix in CONFIGURE["prefix"]:
        if prefix in content[0:7] and author != "Memento":
            with open(f"log_{dt.today().strftime('%d-%m-%Y')}.json",
                      'a',
                      encoding="utf-8") as log_dump:
                json.dump(log,
                          log_dump,
                          indent=4,
                          ensure_ascii=False)
                log_dump.write(",\n")
            print(log)
            response_answer: bool = False
            for item in RESPONSE_CONTROLLER:
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
            if response_answer is False:
                response_answer = await open_ai_integrate(client,
                                                          message)

client.run(CONFIGURE["discord_token"])
