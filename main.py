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
from database.queries import get_all_active_websites_sources
from tgbot.bot import run_bot, send_negative_publication_notification
from analyzer.publication_processor import get_assesment, check_university_mentions, check_keyword_mentions
from analyzer.sentiment_analyze import predict
from parser.websites_parser import parse_big_radio_news, parse_hibiny_news, parse_tv21news_info

import random




#data = get_posts(VK_PUBLICS_NAMES["murmansk"], 10)
#print(data)
async def parse_publications():
    print("Starting parsing...")
    website_sources = await get_all_active_websites_sources()
    news = []
    for source in website_sources:
        if source["sname"] == "Хибины.ру":
            n = parse_hibiny_news()
            news.extend(n)
        elif source["sname"] == "Большое Радио":
            n = parse_big_radio_news()
            news.extend(n)
        else:
            n = parse_tv21news_info()
    
    vk_sources = await get_all_active_vk_sources()
    print(f"vk sources - {len(vk_sources)}")
    posts = await vk_parser.parse_vk(80,vk_sources)
    tg_sources = await get_all_active_tg_sources()
    print(f"tg sources - {len(tg_sources)}")
    tg_posts = await parse_tg_async(10, tg_sources)
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
    for n in news:
        await insert_publication(pid = int(time.time() * 1000) + random.randint(0, 999),
                                 text=n["text"],
                           url=n['post_url'],
                           post_date=n['post_date'],
                           sid=n['sid'],
                           parse_date=n['parse_date'],
                           views = n["views"],
                           likes = n["likes"],
                           comments = n["comments"],
                           reposts = n["reposts"])
    print(f"Собрано {len(posts)} публикаций ВК")
    print(f"Собрано {len(tg_posts)} публикаций ТГ")
    print(f"Собрано {len(news)} публикаций с Вебсайтов")

async def analyze_and_notify():
    """Анализ публикаций и отправка уведомлений"""
    logging.info("Checking for negative publications")
    last_publications = await get_last_publications(60)  
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
            await asyncio.sleep(60) 
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