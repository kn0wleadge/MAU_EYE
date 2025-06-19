import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import re
import datetime
import time
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
    r = requests.get("https://www.tv21.ru/news", headers=tv21_headers)
    response_text = r.text
    news_container_start_index = response_text.find('<div class="news grid-1 js-news-container">')
    news_container_end_index = response_text.find('<div class="calendar-title">Календарь новостей</div>')
    response_text = response_text[news_container_start_index:news_container_end_index]
    for i in range(response_text.count("href")):
        href_index = response_text.find("href") + 6 
        href_end_index = response_text.find('<img srcset="') - 19
        url = response_text[href_index:href_end_index]
        news_urls.append("https://www.tv21.ru" + url)
        response_text = response_text[href_end_index + 25:]
    print(f'NEWS URL --------------{news_urls}')
    return news_urls
def parse_tv21news_info():
    news_info = []
    #r = requests.get(news, headers=tv21_headers)
    #print(r.text)

def parse_hibiny_news():
    base_url = "https://www.hibiny.ru"
    news_page_url = "https://www.hibiny.ru/murmanskaya-oblast/news/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Получаем главную страницу с новостями
        response = requests.get(news_page_url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        # Регулярное выражение для поиска блоков с новостями
        news_blocks = re.findall(r'<div class="news_list" id="item-\d+">.*?<div class="clearer-left"></div>\s*</div>', html_content, re.DOTALL)
        
        news_data = []
        
        for block in news_blocks:
            try:
                # Извлекаем ссылку на новость
                link_match = re.search(r'<h2><a href="([^"]+)"', block)
                if not link_match:
                    continue
                    
                news_url = base_url + link_match.group(1)
                
                # Переходим на страницу новости
                news_response = requests.get(news_url, headers=headers)
                news_response.raise_for_status()
                news_html = news_response.text
                
                # Извлекаем ID новости
                pid_match = re.search(r'item-(\d+)', news_url)
                pid = pid_match.group(1) if pid_match else "0"
                
                # Извлекаем текст новости
                text_match = re.search(r'<div class="margintop16" id="DivText">(.*?)<div id="EndText">', news_html, re.DOTALL)
                text = re.sub(r'<[^>]+>', '', text_match.group(1)).strip() if text_match else ""
                
                # Извлекаем дату публикации
                date_match = re.search(r'<div class="p14l">(.*?)</div>', news_html)
                date_text = date_match.group(1).strip() if date_match else ""
                
                # Преобразуем дату в timestamp
                post_date = parse_date_hibini(date_text)
                
                # Собираем данные в словарь
                news_dict = {
                        "pid": int(pid) if pid else 0,  # Преобразуем в int
                        "text": text,
                        "post_url": news_url,
                        "post_date": int(post_date.timestamp()),  # Уже число (timestamp)
                        "sid": 1,  # Преобразуем в int
                        "parse_date": int(time.time()),  # Уже число (timestamp)
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "reposts": 0
                    }
                
                news_data.append(news_dict)
                
            except Exception as e:
                print(f"Ошибка при обработке новости: {e}")
                continue
                
        return news_data
        
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []

def parse_date_hibini(date_str):
    """Парсит дату из строки в объект datetime"""
    now = datetime.datetime.now()
    
    if "Сегодня" in date_str:
        time_part = re.search(r'в (\d{1,2}:\d{2})', date_str)
        if time_part:
            time_obj = datetime.datetime.strptime(time_part.group(1), "%H:%M").time()
            return datetime.datetime.combine(now.date(), time_obj)
    
    elif "вчера" in date_str.lower():
        time_part = re.search(r'в (\d{1,2}:\d{2})', date_str)
        if time_part:
            time_obj = datetime.datetime.strptime(time_part.group(1), "%H:%M").time()
            yesterday = now - datetime.timedelta(days=1)
            return datetime.datetime.combine(yesterday.date(), time_obj)
    
    else:
        date_match = re.search(r'(\d{1,2}) (\w+) в (\d{1,2}:\d{2})', date_str)
        if date_match:
            day = int(date_match.group(1))
            month_str = date_match.group(2).lower()
            time_str = date_match.group(3)
            
            month_map = {
                'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
                'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
                'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
            }
            
            if month_str in month_map:
                time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
                return datetime.datetime(now.year, month_map[month_str], day, time_obj.hour, time_obj.minute)
    
    return now


def parse_big_radio_news():
    base_url = "https://big-radio.ru"
    news_page_url = "https://big-radio.ru/news"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Получаем главную страницу с новостями
        response = requests.get(news_page_url, headers=headers)
        response.raise_for_status()
        html_content = response.text
        
        # Регулярное выражение для поиска блоков с новостями
        news_blocks = re.findall(r'<div class="block clearfix">.*?<div class="block-text">.*?</div>', html_content, re.DOTALL)
        
        news_data = []
        
        for block in news_blocks[:5]:  # Ограничимся 5 новостями для примера
            try:
                # Извлекаем ссылку на новость
                link_match = re.search(r'<a href="(/news/\d+/\d+/\d+/\d+)"', block)
                if not link_match:
                    continue
                    
                news_url = base_url + link_match.group(1)
                
                # Переходим на страницу новости
                news_response = requests.get(news_url, headers=headers)
                news_response.raise_for_status()
                news_html = news_response.text
                
                # Извлекаем ID новости из URL
                pid_match = re.search(r'/(\d+)/?$', news_url)
                pid = pid_match.group(1) if pid_match else "0"
                
                # Извлекаем заголовок новости
                title_match = re.search(r'<h2 class="news-title".*?>(.*?)</h2>', news_html, re.DOTALL)
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ""
                
                # Улучшенное извлечение текста новости
                text_match = re.search(r'<div class="news-text".*?>(.*?)</div>', news_html, re.DOTALL)
                if text_match:
                    # Удаляем все HTML-теги, но сохраняем текст
                    text = re.sub(r'<[^>]+>', ' ', text_match.group(1))
                    # Удаляем лишние пробелы и переносы строк
                    text = ' '.join(text.split())
                else:
                    text = ""
                
                # Извлекаем дату публикации
                date_match = re.search(r'<div class="news-date">(.*?)</div>', news_html)
                date_text = date_match.group(1).strip() if date_match else ""
                
                # Преобразуем дату в timestamp
                post_date = parse_big_radio_date(date_text)
                
                # Собираем данные в словарь
                news_dict = {
                                "pid": int(pid) if pid else 0,  # Преобразуем в int
                                "text": title,
                                "post_url": news_url,
                                "post_date": int(post_date.timestamp()),  # Уже число (timestamp)
                                "sid": 3,  # Преобразуем в int
                                "parse_date": int(time.time()),  # Уже число (timestamp)
                                "likes": 0,
                                "views": 0,
                                "comments": 0,
                                "reposts": 0
                            }     
                
                news_data.append(news_dict)
                
            except Exception as e:
                print(f"Ошибка при обработке новости {news_url}: {e}")
                continue
                
        return news_data
        
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []

def parse_big_radio_date(date_str):
    try:
        # Формат даты на сайте: "18.06.2025, 18:18"
        date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4}), (\d{2}):(\d{2})', date_str)
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = int(date_match.group(3))
            hour = int(date_match.group(4))
            minute = int(date_match.group(5))
            
            return datetime.datetime(year, month, day, hour, minute)
    except Exception as e:
        print(f"Ошибка при парсинге даты: {e}")
    
    return datetime.datetime.now()
    
# Пример использования с более подробным выводом
if __name__ == "__main__":
    print("Начинаем парсинг новостей с Big Radio...")
    news = parse_big_radio_news()
    print(f"Найдено новостей: {len(news)}")
    
    for i, item in enumerate(news, 1):
        print(f"\nНовость #{i}")
        print(f"ID: {item['pid']}")
        print(f"URL: {item['post_url']}")
        print(f"Дата: {datetime.datetime.fromtimestamp(int(item['post_date']))}")
        print(f"Заголовок: {item.get('title', '')}")
        print(f"Текст: {item['text'][:200]}...")  # Выводим первые 200 символов текста
        print("-" * 80)