from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).parent

YOUTUBE_KEY = config('YOUTUBE')
DISCORD_KEY = config('DISCORD')
MAIN_CHANNEL = config('MAIN_CHANNEL', cast=int)
DISCROD_PREFIXES = 'мементо'
AI_ID = config('AI_ID')
MODEL_URI = F'gpt://{AI_ID}/yandexgpt'
AI_KEY = config('AI_KEY')
AI_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

FORMAT = '%d.%m.%Y %H:%M:%S'
BD_FORMAT = '%d.%m'
LOGS_DIR = BASE_DIR / 'logs'
LOG_FILE = 'LOADER_log.log'


BASE_HEADERS = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/111.0.0.0 Safari/537.36',
}
BASE_AI_HEADERS = {
    'Content-Type': 'application/json',
    "Authorization": f'Api-Key {AI_KEY}'
}

CONGRATS_LIST = [
    'Поздравляю! Любви и радости желаю :)',
    'Бесконечно растущей творческой потенции тебе, товарищ!',
    'Да останешься ты таким же, какой ты есть. И пусть ничего не болит!',
    'Встретились после долгой разлуки старые друзья... '
    'Решили они стол организовать, '
    'отметить встречу. Накрыли, разные явства '
    'на столе присутствуют: кабан на вертеле, '
    'сливы, прочие фрукты, куча салатов и т.п. '
    'В общем, первый произносит тост: \n'
    '- Выпьем же, друг, за удачу!\n'
    'Посидели еще чуть чуть, первый опять произносит тост: \n'
    '- Выпьем же, друг, за удачу!\n'
    'Так за удачу они выпили еще раз 7. Второй не выдержал: \n'
    '- Друг мой, а почему мы с тобой пьем лишь за удачу, '
    'но ни разу за здоровье?\n'
    'А первый ему и отвечает:\n'
    '- Видишь этого кабана на столе? У него с утра было ТАКОЕ здоровье... '
    'А вот удача обошла его стороной.\n'
    'Вот чтоб и в твоей жизни удача была всегда на твоей стороне :) С ДР!',
]
