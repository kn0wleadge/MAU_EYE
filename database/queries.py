import os
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update

from database.models import async_session
from database.models import VkPostsRaw


async def get_post(url:str):
    post = None
    async with async_session() as session:
        try:
            post = await session.scalar(select(VkPostsRaw).where(VkPostsRaw.purl == url))
        except Exception as e:
            print(f'Error during select from VkPostsRaw - {e}')
    return post

async def insert_post(text:str, url:str, parse_time:DateTime, group:str):
    async with async_session() as session:
        try:
            if (await get_post(url()) != None):
                await session.execute(insert(VkPostsRaw).values(ptext = text, purl = url, pparsetime = parse_time, pgroup = group))
                await session.commit()
        except Exception as e:
            print(f'Error during insterting into VkPostsRaw - {e}')


        