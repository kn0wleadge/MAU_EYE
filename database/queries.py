import os
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update
import datetime
import json
from database.models import async_session
from database.models import VkPostsRaw, WebsiteNewsRaw


async def get_vk_post(id):
    post = None
    async with async_session() as session:
        try:
            post = await session.scalar(select(VkPostsRaw).where(VkPostsRaw.pid == id))
        except Exception as e:
            print(f'Error during select from VkPostsRaw - {e}')
    
    return post

async def insert_vk_post(text:str, url:str, post_date:DateTime, group:str, parse_date:DateTime, id = -1):
    # ЗАРЕФАКТОРИТЬ ДУБЛИРОВАНИЕ ИФОВ
    async with async_session() as session:
        try:
            if id == -1:
                if (await get_vk_post(id) == None):
                    await session.execute(insert(VkPostsRaw).values(ptext = text,
                                                                     purl = url, 
                                                                     pdate = datetime.datetime.fromtimestamp(int(post_date)),
                                                                       pgroup = group, 
                                                                       parse_date = datetime.datetime.fromtimestamp(int(parse_date))))
                    await session.commit()
                else:
                    print(f'Post already exists in DB!')
            else:
                if (await get_vk_post(id) == None):
                    await session.execute(insert(VkPostsRaw).values(pid = id,
                                                                    ptext = text,
                                                                      purl = url,
                                                                        pdate = datetime.datetime.fromtimestamp(int(post_date)),
                                                                          pgroup = group, 
                                                                          parse_date = datetime.datetime.fromtimestamp(int(parse_date))))
                    await session.commit()
                else:
                    print(f'Post already exists in DB!')
        except Exception as e:
            print(f'Error during insterting into VkPostsRaw - {e}')

async def get_wnews(url:str):
    news = None
    async with async_session() as session:
        try:
            news = await session.scalar(select(WebsiteNewsRaw).where(WebsiteNewsRaw.nurl == url))
        except Exception as e:
            print(f'Error during select from WebsiteNewsRaw - {e}')
    
    return news
async def insert_wnews(text:str, url:str, post_date:DateTime, parse_date:DateTime,website_name:str):
    async with async_session() as session:
        try:
            if (await get_wnews(url) == None):
                await session.execute(insert(WebsiteNewsRaw).values(ntext = text,
                                                                    nurl = url,
                                                                    ndate = datetime.datetime.fromtimestamp(int(post_date)),
                                                                    parse_date = datetime.datetime.fromtimestamp(int(parse_date)),
                                                                    website_name = website_name))
                await session.commit()
            else:
                print(f'News already exists in DB!')
        except Exception as e:
            print(f'Error during insterting into WebsiteNewsRaw - {e}')
        