import json

import requests as r

from configure import CONFIGURE


def youtube_finder(query: str) -> str:

    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/111.0.0.0 Safari/537.36',
    }

    req = r.get('https://www.googleapis.com/youtube/v3/search?part=snippet&'
                f'q={query}&type=video&key={CONFIGURE["youtube_key"]}',
                headers)

    with open('req.json', 'w', encoding='utf-8') as req_file:
        req_file.write(req.text)
    with open('req.json', encoding='utf-8') as req_file:
        responce = json.load(req_file)

    video_id = responce['items'][0]['id']['videoId']

    link = f'https://youtu.be/{video_id}'
    return link


if __name__ == '__main__':
    query = input("Введите запрос: ")
    query = query.replace(" ", "+")
    link = youtube_finder(query)
    print(link)
