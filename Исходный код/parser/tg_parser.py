from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from pyrogram import Client
import datetime
import logging
import asyncio
import time
# Ваши данные API
api_id = 23210274
api_hash = 'b9c5ddc1fce4ccae6436cf2cf52a3fd9'
phone = '+79600274739'
app = Client("my_account", api_id=api_id, api_hash=api_hash)
# Название канала (например, 't.me/channelname' - используйте 'channelname')
channel_username = 'region_m51'
async def get_chat_info_async(domain):
    async with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
        chat = await app.get_chat(domain)
        return {
            "id": chat.id,
            "name": chat.title
        }

def get_chat_info(domain):
    return asyncio.run(get_chat_info_async(domain))

async def parse_tg_async(posts, sources: list):
    tg_posts = []
    app = Client("my_account", api_id=api_id, api_hash=api_hash)
    await app.start()
    
    try:
        #i = 1
        for source in sources:
            async for post in app.get_chat_history(source["sdomain"], limit=posts):
                print(f"Parsing {source['sname']} post id - {post.id}")
                #i+=1
                #print(post)
                if post.caption is not None or post.text is not None:
                    reactions = 0
                    if post.reactions:
                        for reaction in post.reactions.reactions:
                            reactions += reaction.count
                    
                        try:
                            replies = await app.get_discussion_replies_count(source["sdomain"], post.id)
                        except Exception as e:
                            logging.warning(f"Failed to get replies count: {e}")
                            replies = 0
                    else:
                        replies = 0
                    post_info = {
                        "pid": post.id,
                        "text": post.caption or post.text,
                        "post_url": f"https://t.me/{source['sdomain']}/{post.id}",
                        "post_date": str(int(post.date.timestamp())),
                        "sid": source["sid"],
                        "parse_date": str(int(datetime.datetime.now().timestamp())),
                        "likes": reactions,
                        "views": post.views if hasattr(post, "views") else 0,
                        "comments": replies,
                        "reposts": post.forwards if hasattr(post, "forwards") else 0
                        }
                    logging.info(f"parsing post with url - https://t.me/{source['sdomain']}/{post.id}")
                    tg_posts.append(post_info)
                    await asyncio.sleep(0.5)  # Используем asyncio.sleep вместо time.sleep
    finally:
        await app.stop()  # Явная остановка клиента
    
    return tg_posts

def parse_tg(posts, sources: list):
    return asyncio.run(parse_tg_async(posts, sources))

def parse_tg(posts, sources: list):
    return asyncio.run(parse_tg_async(posts, sources))

if __name__ == "__main__":
    info = get_chat_info("region_m51")



