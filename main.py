#!/usr/bin/python3
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot
from discord.message import Message

from memento.configure import (DISCORD_KEY, DISCROD_PREFIXES, FORMAT, LOG_FILE,
                               LOGS_DIR)
from memento.discord_functions import birthday, run_command
from memento.functions import clear_context

logger = logging.getLogger('MEMENTO')
Path(LOGS_DIR).mkdir(exist_ok=True)
handler = TimedRotatingFileHandler(
    filename=Path(LOGS_DIR) / Path(LOG_FILE),
    interval=1, when='midnight', backupCount=90,
    encoding='utf-8'
)
handler.suffix = f'{handler.suffix}.log'
formatter = logging.Formatter(
    '[%(asctime)s][%(name)s] %(levelname)s: %(message)s',
    FORMAT
)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

intents = discord.Intents.all()
intents.message_content = True
client = Bot(command_prefix=DISCROD_PREFIXES, intents=intents)


@client.event
async def on_ready():
    logger = logging.getLogger('MEMENTO.STARTUP')
    logger.info('Бот начал работу.')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_context, 'interval', hours=1)
    trigger = CronTrigger(hour='0', minute='14')
    scheduler.add_job(birthday, trigger=trigger, args=(client,))
    scheduler.start()
    await birthday(client)


@client.event
async def on_message(message: Message):
    logger = logging.getLogger('MEMENTO.MESSAGE')
    if (message.author.name != 'Memento'  # если убрать - будет фани
       and DISCROD_PREFIXES in message.content.lower()):
        logger.warning(f'Пришло сообщение от `{message.author.name}`.')
        await run_command(client, message)

client.run(DISCORD_KEY)
