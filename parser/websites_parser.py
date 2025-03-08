import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup

tv21_headers = {
    "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0 (Edition std-2)"
}
WEBSITES_URLS = {
    'tv21': 'https://www.tv21.ru/news',
    'mvestnik' : 'https://www.mvestnik.ru/newslent/',
    'murman' : 'https://murman.tv/ct-n-2--news',
    'vmurmansk' : 'https://vmnews.ru/novosti',
}
def parse_news(url:str, headers:dict):
    r = requests.get(url, headers=headers)
    return r

# Запуск асинхронного кода
if __name__ == "__main__":
    try:
        news = parse_news(WEBSITES_URLS["tv21"],tv21_headers)

        print(news.text)

    except Exception as e:
        print(e)