import asyncio
import aiohttp
from bs4 import BeautifulSoup
import datetime
import re
from urllib.parse import urljoin # Though not collecting images, base_url might be useful for other relative links if needed in future.
import requests


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
def get_tv21news_urls():
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
        news_urls.append("https://www.tv21.ru" + url)
        response_text = response_text[href_end_index + 25:]
    print(f'NEWS URL --------------{news_urls}')
    return news_urls
async def fetch_page(session, url):
    """Асинхронно загружает HTML-содержимое одной страницы."""
    try:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            response.raise_for_status() # Проверка на ошибки HTTP
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Ошибка при загрузке URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при загрузке URL {url}: {e}")
        return None

def parse_single_page_data(html_content, url, website_name):
    """Парсит HTML-содержимое для извлечения необходимых данных."""
    parse_time = datetime.datetime.now().timestamp()
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    result = {
        'ntext': None,
        'nurl': url,
        'ndate': None,
        'parse_date': datetime.datetime.now().isoformat(),
        'website_name': website_name
    }

    # Извлечение даты публикации (ndate)
    try:
        date_tag = soup.find('span', class_='news-detail__date')
        if date_tag:
            result['ndate'] = date_tag.get_text(strip=True)
        else:
            time_tag = soup.find('time')
            if time_tag and time_tag.get('datetime'):
                result['ndate'] = time_tag.get('datetime')
            elif time_tag:
                result['ndate'] = time_tag.get_text(strip=True)
            else:
                meta_items = soup.find_all(['div', 'span'], class_=re.compile(r'(date|time|meta)', re.I))
                for item in meta_items:
                    date_text = item.get_text(strip=True)
                    match = re.search(r'\d{2}\.\d{2}\.\d{4}(?:, \d{2}:\d{2})?', date_text)
                    if match:
                        result['ndate'] = match.group(0)
                        break
    except Exception as e:
        print(f"Ошибка при парсинге даты для URL {url}: {e}")

    # Извлечение текста новости (ntext)
    try:
        content_div = soup.find('div', class_='news-detail__text typography')
        if not content_div:
            content_div = soup.find('div', class_='news-detail__text')
        if not content_div:
            content_div = soup.find('div', itemprop='articleBody')
        if not content_div:
            content_div = soup.find('article')
        if not content_div:
            content_div = soup.find('div', class_=re.compile(r'(article-content|post-content|entry-content|main-content|story-body|text)', re.I))

        if content_div:
            for el_to_remove in content_div.find_all(['script', 'style', 'iframe', 'aside', 'nav', 'form', 'button']):
                el_to_remove.decompose()
            for el_to_remove in content_div.find_all(class_=re.compile(r'(related|comments|share|social|also|promo|sidebar|banner|ad|gallery|image|video|figure)', re.I)):
                el_to_remove.decompose()
            
            article_parts = []
            for element in content_div.find_all(['p', 'blockquote', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol'], recursive=True):
                current_text = ""
                if element.name in ['ul', 'ol']:
                    list_items_text = []
                    for li in element.find_all('li', recursive=False):
                        li_text = li.get_text(separator=' ', strip=True)
                        if li_text:
                            list_items_text.append(f"- {li_text}")
                    if list_items_text:
                        current_text = '\n'.join(list_items_text)
                elif element.name == 'blockquote':
                    quote_text = element.get_text(separator=' ', strip=True)
                    if quote_text:
                        current_text = f"> {quote_text}"
                else: # p, h2-h6
                    text_content = element.get_text(separator=' ', strip=True)
                    if text_content:
                        current_text = text_content
                
                if current_text:
                    is_duplicate_from_list = False
                    if article_parts and element.name == 'p':
                        if any(current_text in part for part in article_parts if part.startswith("-")):
                            is_duplicate_from_list = True
                    if not is_duplicate_from_list:
                        article_parts.append(current_text)
            
            if article_parts:
                full_text = '\n\n'.join(article_parts)
                lines = full_text.split('\n\n')
                cleaned_lines = []
                for line_content in lines:
                    if "Фото создано при помощи ИИ" in line_content and line_content.strip() == "Фото создано при помощи ИИ":
                        continue
                    if line_content.strip().startswith("Читайте также:"):
                        continue
                    cleaned_lines.append(line_content)
                result['ntext'] = '\n\n'.join(cleaned_lines) if cleaned_lines else None
            else:
                raw_text = content_div.get_text(separator='\n', strip=True)
                raw_lines = raw_text.split('\n')
                final_raw_lines = [line.strip() for line in raw_lines if line.strip() and not line.strip().startswith("Читайте также:") and not "Фото создано при помощи ИИ" in line.strip()]
                result['ntext'] = '\n'.join(final_raw_lines) if final_raw_lines else None
        else:
            print(f"Не удалось найти основной контент для URL {url}")

    except Exception as e:
        print(f"Ошибка при парсинге текста для URL {url}: {e}")
    date_str = result['ndate']
    new_date = datetime.datetime.strptime(date_str, "%d.%m.%Y, %H:%M")
    timestamp = int(datetime.datetime.timestamp(new_date))
    result['ndate'] =  timestamp
    result['parse_date'] = parse_time
    return result

async def fetch_and_parse_single_page(session, url, website_name):
    """Асинхронно загружает и парсит одну страницу."""
    html_content = await fetch_page(session, url)
    if html_content:
        return parse_single_page_data(html_content, url, website_name)
    return {
        'ntext': None,
        'nurl': url,
        'ndate': None,
        'parse_date': datetime.datetime.now().isoformat(),
        'website_name': website_name,
        'error': 'Failed to fetch page'
    }

async def parse_multiple_news_async(urls, website_name):
    """
    Асинхронно собирает информацию со списка новостных страниц.
    Возвращает список словарей, каждый из которых содержит:
    'ntext': Текст новости (str_or_None)
    'nurl': Ссылка на новость (str)
    'ndate': Дата публикации новости (str_or_None)
    'parse_date': Дата сбора новости (str, ISO format)
    'website_name': Название новостного портала (str)
    """
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_parse_single_page(session, url, website_name) for url in urls]
        parsed_data_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        for data in parsed_data_list:
            if isinstance(data, Exception):
                # Можно логировать ошибку более детально или обрабатывать по-другому
                print(f"Ошибка при обработке URL в asyncio.gather: {data}")
                # Добавляем информацию об ошибке, если нужно
                # results.append({'nurl': 'unknown', 'error': str(data), ...})
            elif data:
                results.append(data)
    return results

if __name__ == '__main__':
    website = "tv21.ru"
    parse_urls = parse_tv21news_urls()
    results_list = asyncio.run(parse_multiple_news_async(parse_urls, website))
    print("\nРезультаты парсинга:")
    for idx, item in enumerate(results_list):
        print(f"--- Новость {idx+1} ---")
        print(f"  URL: {item.get('nurl')}")
        print(f"  Дата публикации: {item.get('ndate')}")
        print(f"  Дата парсинга: {item.get('parse_date')}")
        print(f"  Сайт: {item.get('website_name')}")
        text_preview = item.get('ntext')
        if text_preview:
            print(f"  Текст (превью): {text_preview[:]}...")
        else:
            print(f"  Текст: None")
        if item.get('error'):
             print(f"  Ошибка: {item.get('error')}")
        print("---------------------")

