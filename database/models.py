import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import BigInteger, Integer, String,DateTime, ForeignKey, Boolean
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
class Publication(Base):
    __tablename__ = "publication"
    pid:Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ptext =  mapped_column(String(15555))
    purl=  mapped_column(String(200))
    pdate = mapped_column(DateTime)
    psource = mapped_column(String(100))
    parse_date = mapped_column(DateTime)
    assesment = mapped_column(String(20))
    mau_mentioned = mapped_column(Boolean)
    def __str__(self):
        return (
            f"Publication(pid={self.pid}, "
            f"ptext='{self.ptext[:50]}', "
            f"url={self.purl}, "
            f"pdate='{self.pdate}...', "  # Первые 50 символов текста
            f"psource='{self.psource}', "
            f"parse_date='{self.parse_date}',"
            f"assesment= '{self.assesment}',"
            f"mau_mentioned={self.mau_mentioned})"
        )

class Source(Base):
    __tablename__ = "Sources"
    sid:Mapped[int] = mapped_column(primary_key=True, autoincrement= True)
    sname = mapped_column(String(100))
    surl = mapped_column(String(200))
    sdomain = mapped_column(String(100))
    source_type = mapped_column(String(20))  # 'vk', 'telegram', 'website'
    is_active = mapped_column(Boolean, default=True)
    added_date = mapped_column(DateTime)
    
engine = create_async_engine(url=os.getenv("POSTGRESQL_URL"))
async_session = async_sessionmaker(engine)

async def async_main():
    async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)













