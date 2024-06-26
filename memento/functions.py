import logging
from datetime import datetime as dt
from datetime import timedelta as td

import requests as r
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from .configure import BASE_HEADERS, YOUTUBE_KEY
from .db import ENGINE, Messages, User


async def check_empty(data: list) -> bool:
    return bool(list(filter(None, data)))


async def clear_context():
    logger = logging.getLogger('MEMENTO.functions.cleaner')
    async_session = async_sessionmaker(ENGINE, expire_on_commit=False)
    async with async_session() as session:
        all_context = (
            await session.scalars(select(Messages).where(
                Messages.user_messages != ''))).all()
        for item in all_context:
            user: User = (await session.scalars(
                select(User.name).where(User.id == item.user))).one()
            logger.warning(
                f'Обнаружен старый контекст сообщений для `{user}`.')
            delta: td = dt.now() - item.time_last_user_message
            if (delta.seconds // 60) >= 120:
                item.user_messages = ''
                item.ai_messages = ''
                await session.commit()


async def compile_data(users: dict) -> User:
    for key, value in users.items():
        async_session = async_sessionmaker(ENGINE, expire_on_commit=False)
        query = select(User).where(User.discord_id == value)
        async with async_session() as session:
            if not (await session.scalars(query)).one_or_none():
                user = {'discord_id': value,
                        'birthdate': dt.strptime(key, '%d-%m')}
                session.add(User(**user))
                await session.commit()
    async with async_session() as session:
        for user in (await session.scalars(select(User))).all():
            if not (await session.scalars(
                 select(Messages).where(
                     Messages.user == user.id))).one_or_none():
                session.add(Messages(**{'user': user.id}))
        await session.commit()


async def youtube_finder(query: str) -> str:
    res = r.get(
        'https://www.googleapis.com/youtube/v3/search?part=snippet&'
        f'q={query}&type=video&key={YOUTUBE_KEY}', headers=BASE_HEADERS).json()

    return 'https://youtu.be/{0}'.format(
        res['items'][0]['id']['videoId'])
