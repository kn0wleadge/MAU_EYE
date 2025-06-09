from dotenv import load_dotenv
load_dotenv()
import requests
import asyncio
import os
import datetime
import logging
import time
from fastapi import FastAPI
from tgbot.bot import bot,dp
from flask import Flask, render_template, jsonify, request
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update

import parser.vk_parser as vk_parser
from parser.tg_parser import parse_tg_async
import parser.async_website_parsers as website_parsers
from parser.async_website_parsers import parse_multiple_news_async
from database.models import async_main, async_session, Publication, Source
from database.queries import insert_vk_post,insert_publication, add_assesment,get_all_active_tg_sources, get_last_publications,get_all_active_vk_sources, add_mention, all_users, get_keywords, add_keyword_in_publication, get_publications_keyword
from tgbot.bot import run_bot, send_negative_publication_notification
from analyzer.publication_processor import get_assesment, check_university_mentions, check_keyword_mentions
from analyzer.sentiment_analyze import predict
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"








#data = get_posts(VK_PUBLICS_NAMES["murmansk"], 10)
#print(data)
async def parse_publications():
    print("Starting parsing...")
    vk_sources = await get_all_active_vk_sources()
    print(f"vk sources - {len(vk_sources)}")
    posts = await vk_parser.parse_vk(100,vk_sources)
    news_links = website_parsers.get_tv21news_urls()
    news = await parse_multiple_news_async(news_links, "tv21")
    tg_sources = await get_all_active_tg_sources()
    print(f"tg sources - {len(tg_sources)}")
    tg_posts = await parse_tg_async(30, tg_sources)
    #TODO - Зарефакторить словари, которые собирают парсеры, чтобы они были одного формата
    # for n in news:
    #     await insert_publication(text=n["ntext"],
    #                        url=n['nurl'],
    #                        post_date=n['ndate'],
    #                        source=n['website_name'],
    #                        parse_date=n['parse_date'])
    for post in posts:
        await insert_publication(pid = post["pid"],
                                 text = post["text"],
                           url=post['post_url'],
                           post_date=post['post_date'],
                           sid=post['sid'],
                           parse_date=post['parse_date'],
                           views = post["views"],
                           likes = post["likes"],
                           comments = post["comments"],
                           reposts = post["reposts"])
    
    for post in tg_posts:
        await insert_publication(pid = post["pid"],
                                 text=post["text"],
                           url=post['post_url'],
                           post_date=post['post_date'],
                           sid=post['sid'],
                           parse_date=post['parse_date'],
                           views = post["views"],
                           likes = post["likes"],
                           comments = post["comments"],
                           reposts = post["reposts"])
    print(f"Собрано {len(posts)} публикаций ВК")
    print(f"Собрано {len(tg_posts)} публикаций ТГ")
    #await insert_post("TEXT", "URL", datetime.datetime.now(),"GROUP")

async def analyze_and_notify():
    """Анализ публикаций и отправка уведомлений"""
    logging.info("Checking for negative publications")
    last_publications = await get_last_publications(60)  # Используем вашу существующую функцию
    publications_with_mentions = []
    keywords = await get_keywords()
    for publication in last_publications:
        result_keywords = []
        for keyword in keywords:
            #university_mentioned = check_university_mentions(publication.ptext)
            keyword_mentioned = check_keyword_mentions(keyword.word, publication.ptext)
            if (keyword_mentioned == True):
                result_keywords.append(keyword.word)
        flag = False
        if (len(result_keywords) != 0):
            flag = True
            for keyword in result_keywords:
                await add_keyword_in_publication(publication.pid,keyword)
        if (flag == True):
            publications_with_mentions.append(publication)
            await add_mention(publication.purl,True)
    for publication in publications_with_mentions:
        #print(f"Getting assesment in publication - {publication.ptext}")
        prediction = predict(publication.ptext)
        if (publication.assesment == None):
            await add_assesment(publication.purl, prediction["assesment"])
            print(f"Prediction - {prediction}")
            if prediction["assesment"] == "negative":
                users = await all_users() 
                print(f"Publication {publication.pid} sending notification")
                await send_negative_publication_notification(publication, users)
        else:
            print(f"Publication {publication.pid} already sent")

async def run_monitoring():
    while True:
        try:
            await parse_publications()
            await analyze_and_notify()
            await asyncio.sleep(60)  # Проверка каждую минуту
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
            await asyncio.sleep(60)

async def main():
    monitoring_task = asyncio.create_task(run_monitoring())
    bot_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(monitoring_task, bot_task)
   
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")