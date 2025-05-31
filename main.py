from dotenv import load_dotenv
load_dotenv()
import requests
import asyncio
import os
import datetime
import logging
from fastapi import FastAPI

from flask import Flask, render_template, jsonify, request
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update

import parser.vk_parser as vk_parser
import parser.async_website_parsers as website_parsers
from parser.async_website_parsers import parse_multiple_news_async
from database.models import async_main, async_session, Publication, Source
from database.queries import insert_vk_post,insert_publication, add_assesment, get_last_publications,get_all_active_sources, add_mention


from analyzer.publication_processor import get_assesment, check_university_mentions
from analyzer.sentiment_analyze import predict
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"








#data = get_posts(VK_PUBLICS_NAMES["murmansk"], 10)
#print(data)
#НА ЧЕМ ЗАКОНЧИЛ - СОЗДАЛ ВЫТЯГИВАНИЕ ПОСЛЕДНИХ НОВОСТЕЙ, ДОПИСАТЬ АНАЛИЗ ЭТИХ НОВОСТЕЙ(ФУНКЦИЯ analyze_publications)
async def parse_publications():
    sources = await get_all_active_sources()
    posts = await vk_parser.parse_vk(10,sources)
    news_links = website_parsers.get_tv21news_urls()
    news = await parse_multiple_news_async(news_links, "tv21")
    #TODO - Зарефакторить словари, которые собирают парсеры, чтобы они были одного формата
    # for n in news:
    #     await insert_publication(text=n["ntext"],
    #                        url=n['nurl'],
    #                        post_date=n['ndate'],
    #                        source=n['website_name'],
    #                        parse_date=n['parse_date'])
    for post in posts:
        await insert_publication(text=post["text"],
                           url=post['post_url'],
                           post_date=post['post_date'],
                           source=post['group_name'],
                           parse_date=post['parse_date'])
    
    #await insert_post("TEXT", "URL", datetime.datetime.now(),"GROUP")

async def analyze_publications():
    logging.info("Analyzing last publications")
    last_publications = await get_last_publications(60)
    publications_with_mentions = []
    for publication in last_publications:
            university_mentioned = check_university_mentions(publication.ptext)
            logging.info(f"Mention = {university_mentioned} in publication with url - {publication.purl}")
            await add_mention(publication.purl, university_mentioned)
            if (university_mentioned):
                
                publications_with_mentions.append(publication)
    for publication in publications_with_mentions:
        prediction = predict(publication.ptext)
        logging.info(f"prediction for {publication.purl} - {prediction}")
        await add_assesment(publication.purl, prediction["assesment"])
    
async def run():
    await async_main()
    await parse_publications()
    await analyze_publications()
   
if __name__ == '__main__':
    logging.basicConfig(level = logging.INFO)
    try:
        asyncio.run(run())
        

    except KeyboardInterrupt:
        print("interrupt")