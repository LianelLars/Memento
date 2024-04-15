from datetime import datetime as dt

from decouple import config

YOUTUBE_KEY = config('YOUTUBE')
DISCORD_KEY = config('DISCORD')
AI_KEY = ''
AI_URL = ''
DISCROD_PREFIXES = ['Prefix_1', 'prefix']

BASE_HEADERS = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/111.0.0.0 Safari/537.36',
}


BIRTHDAY_DICT = {
    '01-01': 123123123123123123,
}

CHANNELS = {
    'bots_channel_id': 123123123123123123,
    'major_channel_id': 123123123123123123
}
