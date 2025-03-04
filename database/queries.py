import os
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update

import json
from database.models import async_session
from database.models import VkPostsRaw


async def get_post(id):
    post = None
    async with async_session() as session:
        try:
            post = await session.scalar(select(VkPostsRaw).where(VkPostsRaw.pid == id))
        except Exception as e:
            print(f'Error during select from VkPostsRaw - {e}')
    
    return post

async def insert_post(text:str, url:str, parse_time:DateTime, group:str, id = -1):
    # ЗАРЕФАКТОРИТЬ ДУБЛИРОВАНИЕ ИФОВ
    async with async_session() as session:
        try:
            if id == -1:
                if (await get_post(id) == None):
                    await session.execute(insert(VkPostsRaw).values(ptext = text, purl = url, pparsetime = parse_time, pgroup = group))
                    await session.commit()
                else:
                    print(f'Post already exists in DB!')
            else:
                if (await get_post(id) == None):
                    await session.execute(insert(VkPostsRaw).values(pid = id,ptext = text, purl = url, pparsetime = parse_time, pgroup = group))
                    await session.commit()
                else:
                    print(f'Post already exists in DB!')
        except Exception as e:
            print(f'Error during insterting into VkPostsRaw - {e}')


        