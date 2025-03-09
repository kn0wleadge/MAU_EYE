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
def parse_tv21news_urls():
    news_urls = []
    r = requests.get(WEBSITES_URLS["tv21"], headers=tv21_headers)
    response_text = r.text
    news_container_start_index = response_text.find('<div class="news grid-1 js-news-container">')
    news_container_end_index = response_text.find('<div class="calendar-title">Календарь новостей</div>')
    response_text = response_text[news_container_start_index:news_container_end_index]
    for i in range(response_text.count("href")):
        href_index = response_text.find("href") + 6 
        href_end_index = response_text.find('<img srcset="') - 19
        url = response_text[href_index:href_end_index]
        news_urls.append(url)
        response_text = response_text[href_end_index + 25:]
    print(f'NEWS IRL --------------{news_urls}')
    return news_urls
def parse_tv21news_info(news_url:list):
    news_info = []
    r = requests.get()
# Запуск асинхронного кода
if __name__ == "__main__":
    try:
        news_urls = parse_tv21news_urls()

    except Exception as e:
        print(e)