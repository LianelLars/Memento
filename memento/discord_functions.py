import logging
import re
from datetime import datetime as dt
from random import choice

import requests as r
from discord.ext.commands import Bot
from discord.message import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from .configure import (AI_URL, BASE_AI_HEADERS, BD_FORMAT, CONGRATS_LIST,
                        MAIN_CHANNEL, MODEL_URI)
from .db import ENGINE, Messages, User
from .functions import check_empty, youtube_finder


async def test(client: Bot, message: Message):
    logger = logging.getLogger('MEMENTO.test')
    channel = client.get_channel(message.channel.id)
    await channel.send('Вроде, всё должно работать. Если что - я пишу логи!')
    logger.info('Запрос функции `test`.')


async def hello(client: Bot, message: Message):
    logger = logging.getLogger('MEMENTO.hello')
    channel = client.get_channel(message.channel.id)
    await channel.send(f'Привет, {message.author.name}!')
    logger.info('Запрос функции `hello`.')


async def say_hello(client: Bot, message: Message):
    logger = logging.getLogger('MEMENTO.say_hello')
    channel = client.get_channel(message.channel.id)
    async_session = async_sessionmaker(ENGINE, expire_on_commit=False)
    async with async_session() as session:
        owner: User = (await session.scalars(
            select(User).where(User.is_owner))).one()
    await channel.send(
        'Доброго всем времени суток!\n'
        'Я - Мементо. Бот-помощник для '
        f'{client.get_user(owner.discord_id).mention}.\n'
        'Слежу за его дедлайнами, помогаю не забывать'
        ' определенные вещи, могу найти видосики на ютубе или'
        ' поговорить на любую тему.')
    logger.info('Запрос функции `say_hello`.')


async def find_in_youtube(client: Bot, message: Message):
    '''
    Find video in youtube.
    '''
    logger = logging.getLogger('MEMENTO.youtube')
    channel = client.get_channel(message.channel.id)
    content = message.content.lower().split('видео')[1].strip()
    link = await youtube_finder(content)
    logger.warning(
        f'По запросу от `{message.author.name}` найдено видео {link}')
    await channel.send(f'Я смогла найти вот такое видео: {link}.')


async def birthday(client: Bot, message: Message = None):
    today = dt.today()
    async_session = async_sessionmaker(ENGINE, expire_on_commit=False)
    logger = logging.getLogger('MEMENTO.BIRTHDAY')
    async with async_session() as session:
        users: list[User] = (await session.scalars(select(User))).all()
    channel = client.get_channel(MAIN_CHANNEL)
    user: User = None
    if message:
        channel = client.get_channel(message.channel.id)
        user: list[User] = [
            user for user in users
            if f'{user.discord_id}' in message.content]
    if user:
        logger.warning(f'Найден пользователь {user[0].name}')
        await channel.send(
            f'День рождения у {client.get_user(user[0].discord_id).name} '
            f'{user[0].birthdate.strftime(BD_FORMAT)}.')
        logger.warning(
            f'Пользователь `{message.author.name}` запросил др {user[0].name}')
    else:
        logger = logging.getLogger('MEMENTO.BIRTHDAY.today')
        user: list[User] = [
            user for user in users
            if user.birthdate.strftime(
                BD_FORMAT) == today.strftime(BD_FORMAT)]
        if user:
            logger.warning(f'Сегодня др у `{user[0].name}`.')
            await channel.send(
                f'Сегодня, {today.strftime(BD_FORMAT)}, '
                'день рождения у '
                f'{client.get_user(user[0].discord_id).mention}\n'
                f'{choice(CONGRATS_LIST)}'
            )
        elif message:
            logger.warning(
                'Пользователей, у которых сегодня др, не обнаружено.')
            await channel.send(
                f'Сегодня, {today.strftime(BD_FORMAT)}, '
                'ни у кого ДР нет :)'
            )


async def ya_gpt_message(client: Bot, message: Message):
    async_session = async_sessionmaker(ENGINE, expire_on_commit=False)
    async with async_session() as session:
        author = (await session.scalars(select(User.id).where(
            User.discord_id == message.author.id
        ))).one()
        data = (await session.scalars(select(Messages).where(
            Messages.user == author
        ))).one()
        user_messages: list[str] = data.user_messages.split('|')
        ai_messages: list[str] = data.ai_messages.split('|')
        settings = (
            [{
                'role': 'system',
                'text': 'Ты - персональный ассистент. Пол: женский.'
            }]
        )
        context = []
        check = (
            await check_empty(user_messages)
            and await check_empty(ai_messages)
        )
        if check:
            for usr, ai in list(zip(user_messages, ai_messages)):
                context.append({'role': 'user', 'text': usr})
                context.append({'role': 'assistant', 'text': ai})
        new = [{'role': 'user', 'text': message.content[8:].strip()}]
        prompt = {
            'modelUri': MODEL_URI,
            'completionOptions': {
                'temperature': 0.3,
                'maxTokens': '2000'
            },
            'messages': settings + context + new
        }
        if check:
            user_messages.append(new[0]['text'])
            data.user_messages = '|'.join(user_messages)
        else:
            data.user_messages = new[0]['text']
        res = r.post(AI_URL, headers=BASE_AI_HEADERS, json=prompt)
        answer = res.json()['result']['alternatives'][0]['message']['text']
        if check:
            ai_messages.append(answer)
            data.ai_messages = '|'.join(ai_messages)
        else:
            data.ai_messages = answer
        data.time_last_user_message = dt.now()
        await session.commit()
        channel = client.get_channel(message.channel.id)
        await channel.send(answer)


COMMANDS = [
    {
        'command': hello,
        'words': r'\bпривет\b|\bприв\b|\bдаров\b|\bку\b'
    },
    {
        'command': test,
        'words':
            r'\bработаешь\b|\bвключена\b|\bтест\b|\bотвечаешь\b|'
            r'\bкак дела\b|\bспишь\b|\bты как\b'
    },
    {
        'command': find_in_youtube,
        'words': r'\bнайди видео\b|\bнайти видео\b|\bпокажи видео\b',
    },
    {
        'command': birthday,
        'words': r'\bдр\b|\bдень рождения\b'
    },
    {
        'command': say_hello,
        'words': r'(\bпоздоровайся\b)|(\bрасскажи о себе\b)|(\bкто ты\b)',
    }
]


async def run_command(client: Bot, message: Message):
    content = message.content.lower()[8:]
    is_command = False
    for command in COMMANDS:
        if re.search(command['words'], content):
            await command['command'](client, message)
            is_command = True
            break
    if not is_command:
        await ya_gpt_message(client, message)
