import os
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update
import datetime
import json
import asyncio
import logging
from .models import async_session
from .models import VkPostsRaw, WebsiteNewsRaw, Publication, Source, User
logging.basicConfig()
async def get_user(tg_id):
    async with async_session() as session:
        user = await session.execute(select(User).where(User.tg_id == tg_id))
        print(f"User - {user}")
        return user.scalar()
    
async def add_user(tg_id, rdate):
    async with async_session() as session:
        if (await get_user(tg_id) == None):
            await session.execute(insert(User).values(tg_id = tg_id, registration_date = datetime.datetime.fromtimestamp(int(rdate))))
            await session.commit()
        else:
            print(f"User {tg_id} already exists")
async def all_users():
    async with async_session() as session:
        r = await session.execute(select(User))
        return r.scalars().all()

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
            
async def get_publication(url:str):
    news = None
    async with async_session() as session:
        try:
            news = await session.scalar(select(Publication).where(Publication.purl == url))
        except Exception as e:
            print(f'Error during select from Publication - {e}')
    
    return news
async def delete_publication(url:str):
     async with async_session() as session:
        await session.execute(update(Publication).where(Publication.purl == url).values(deleted = True))
        await session.commit()
async def update_publication(url:str, views, likes, comments,reposts):
    async with async_session() as session:
        await session.execute(update(Publication).where(Publication.purl == url).values(views = views, likes = likes, comments = comments, reposts = reposts))
        await session.commit()
async def insert_publication(pid,text:str, url:str, post_date:DateTime, sid:int, parse_date:DateTime, views:int, likes:int, comments:int, reposts:int):
    async with async_session() as session:
        try:
            if (await get_publication(url) == None):
                await session.execute(insert(Publication).values(pid = pid,ptext = text,
                                                                    purl = url,
                                                                    pdate = datetime.datetime.fromtimestamp(int(post_date)),
                                                                    sid = sid,
                                                                    parse_date = datetime.datetime.fromtimestamp(int(parse_date)),
                                                                    views = views,
                                                                    likes = likes,
                                                                    comments = comments,
                                                                    reposts = reposts,
                                                                    deleted = False
                                                                    ))
                await session.commit()
            else:
                print(f'Publication added already, updating info - {url} ')
                await update_publication(url, views, likes, comments, reposts)

        except Exception as e:
            print(f'Error during insterting into Publication - {e}')

async def add_assesment(url:str, assesment:str):
    async with async_session() as session:
        try:
            if (await get_publication(url) != None):
                await session.execute(update(Publication).where(Publication.purl == url).values(assesment = assesment))
                await session.commit()
            else:
                print(f'ERROR: No publication with url - {url}')
        except Exception as e:
            print(f'Error during adding assesment into Publication - {e}')

async def add_mention(url:str, mau_mention:bool):
    async with async_session() as session:
        try:
            if (await get_publication(url) != None):
                await session.execute(update(Publication).where(Publication.purl == url).values(mau_mentioned = mau_mention))
                await session.commit()
            else:
                print(f'ERROR: No publication with url - {url}')
        except Exception as e:
            print(f'Error during adding mention into Publication - {e}')
                    
async def get_last_publications(minutes: int):
    publications = []
    async with async_session() as session:
        try:
            now = datetime.datetime.now() 
            print(f"Cur date - {now}")
            time_threshold = now - datetime.timedelta(minutes=minutes)

            result = await session.execute(
                select(Publication).where(
                    Publication.parse_date >= time_threshold,
                    Publication.parse_date <= now
                )
            )
            publications = result.scalars().all()
            
        except Exception as e:
            print(f'Error during getting last Publications - {e}')
            await session.rollback()
    return publications

async def insert_source(name, url, source_type, added_date):
    async with async_session() as session:
        await session.execute(insert(Source).values(sname = name, 
                                                    surl = url, source_type = source_type,
                                                    added_date = added_date))
        await session.commit()

async def get_all_active_vk_sources():
    async with async_session() as session:
        logging.info(f"getting VK sources")
        result = (await session.execute(select(Source).where((Source.is_active == True) & (Source.source_type == 'vk')))).scalars().all()
        sources = []
        for row in result:
                source = {"sid":row.sid,
                               "sname":row.sname,
                               "surl":row.surl,
                               "sdomain":row.sdomain,
                               "source_type":row.source_type,
                               "is_active":row.is_active,
                               "added_date":row.added_date}
                sources.append(source)
                logging.info(f"Got source - source ")
        return sources
async def get_all_active_tg_sources():
    async with async_session() as session:
        result = (await session.execute(select(Source).where((Source.is_active == True) & (Source.source_type == 'tg')))).scalars().all()
        sources = []
        for row in result:
                sources.append({"sid":row.sid,
                               "sname":row.sname,
                               "surl":row.surl,
                               "sdomain":row.sdomain,
                               "source_type":row.source_type,
                               "is_active":row.is_active,
                               "added_date":row.added_date})
        return sources
async def test():
    last_publications = await get_last_publications(60)
    print("Printing publications")
    for pub in last_publications:
        print(pub)
if __name__ == "__main__":
    asyncio.run(test())