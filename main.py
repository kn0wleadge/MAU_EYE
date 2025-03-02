from dotenv import load_dotenv
load_dotenv()
import requests
import asyncio
import os
import datetime
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update
class Base(AsyncAttrs, DeclarativeBase):
    pass
class VkPostsRaw(Base):
    __tablename__ = 'vk_posts_raw'
    pid:Mapped[int] = mapped_column(primary_key=True)
    ptext:Mapped[str] = mapped_column(String(15895))
    purl:Mapped[str] = mapped_column(String(150))
    pparsetime = mapped_column(DateTime)
    pgroup:Mapped[str] = mapped_column(String(48))
    def __str__(self):
        return f"VkPostsRaw(pid={self.pid}, text={self.ptext}, url={self.purl}, parse_time={self.pparsetime}, group={self.pgroup})"

from sources import VK_PUBLICS
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"


engine = create_async_engine(url=os.getenv("POSTGRESQL_URL"))
async_session = async_sessionmaker(engine)
async def async_main():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_posts(domain, count):
    domain ="club224630814"
    

    response =requests.get('https://api.vk.com/method/wall.get', 
                            params={
                                'access_token': os.getenv("VK_API_TOKEN"),
                                'v': os.getenv("VK_API_VERSION"),
                                'domain' : domain,
                                'count' : count
                            }
                            )
    data = response.json()['response']['items']
    return data

#data = get_posts(VK_PUBLICS["murmansk"], 10)
#print(data)

async def main():
    await async_main()
    async with async_session() as session:
        data = await session.scalar(select(VkPostsRaw).where(VkPostsRaw.pid == 1))
        print(data)

if __name__ == '__main__':

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("interrupt")