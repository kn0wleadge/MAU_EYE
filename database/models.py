import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import select, insert, update

class Base(AsyncAttrs, DeclarativeBase):
    pass
class VkPostsRaw(Base):
    __tablename__ = 'vk_posts_raw'
    pid:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ptext:Mapped[str] = mapped_column(String(15895))
    purl:Mapped[str] = mapped_column(String(150))
    pdate = mapped_column(DateTime)
    pgroup:Mapped[str] = mapped_column(String(48))
    parse_date = mapped_column(DateTime)
class WebsiteNewsRaw(Base):
    __tablename__ = 'website_news_raw'
    nid:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ntext =  mapped_column(String(15555))
    nurl=  mapped_column(String(200))
    ndate = mapped_column(DateTime)
    parse_date = mapped_column(DateTime)
    website_name =  mapped_column(String(100))

engine = create_async_engine(url=os.getenv("POSTGRESQL_URL"))
async_session = async_sessionmaker(engine)

async def async_main():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)













