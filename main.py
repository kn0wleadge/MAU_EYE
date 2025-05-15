from dotenv import load_dotenv
load_dotenv()
import requests
import asyncio
import os
import datetime

import parser.vk_parser as vk_parser
import parser.async_website_parsers as website_parsers
from parser.async_website_parsers import parse_multiple_news_async
from database.models import async_main, async_session
from database.queries import insert_vk_post, get_vk_post, insert_wnews, get_wnews
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"








#data = get_posts(VK_PUBLICS_NAMES["murmansk"], 10)
#print(data)

async def main():
    await async_main()
    #posts = await vk_parser.parse_vk()
    news_links = website_parsers.get_tv21news_urls()
    news = await parse_multiple_news_async(news_links, "tv21")
    # for post in posts:
    #     await insert_vk_post(id=int(post["id"]),
    #                     text=post["text"],
    #                     url=post["post_url"],
    #                     post_date = post["post_date"],
    #                     group = post["group_name"],
    #                     parse_date=post["parse_date"]
    #                     )
    for n in news:
        await insert_wnews(text=n["ntext"],
                           url=n['nurl'],
                           post_date=n['ndate'],
                           parse_date=n['parse_date'],
                           website_name=n['website_name'])
    #await insert_post("TEXT", "URL", datetime.datetime.now(),"GROUP")


if __name__ == '__main__':

    try:
        asyncio.run(main())
        

    except KeyboardInterrupt:
        print("interrupt")