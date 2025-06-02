from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from pyrogram import Client
import datetime
import logging
import asyncio
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
    async with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
        for source in sources:
            logging.info(f"Parsing {source}")
            async for post in app.get_chat_history(source["sdomain"], limit=posts):
                if post.caption is not None:
                    reactions = 0
                    if post.reactions:
                        for reaction in post.reactions.reactions:
                            reactions += reaction.count
                    
                    # replies count (если доступно)
                    try:
                        replies = await app.get_discussion_replies_count(source["sdomain"], post.id)
                    except Exception as e:
                        logging.warning(f"Failed to get replies count: {e}")
                        replies = 0

                    print(f"chat id - {getattr(post.sender_chat, 'id', 'N/A')} post id - {post.id}")
                    #print(f"post date - {post.date} type - {type(post.date).__name__}")
                    post_info = {
                        "id": post.id,
                        "text": post.caption or post.text,
                        "post_url": f"https://t.me/{source['sdomain']}/{post.id}",
                        "post_date": str(int(post.date.timestamp())),
                        "group_name": post.chat.title if post.chat else None,
                        "parse_date": str(int(datetime.datetime.now().timestamp())),
                        "likes": reactions,
                        "views": post.views if hasattr(post, "views") else 0,
                        "comments": replies,
                        "reposts": post.forwards if hasattr(post, "forwards") else 0
                    }
                    logging.info(f"parsing post with url - https://t.me/{source['sdomain']}/{post.id}")
                    tg_posts.append(post_info)
    return tg_posts

def parse_tg(posts, sources: list):
    return asyncio.run(parse_tg_async(posts, sources))

if __name__ == "__main__":
    info = get_chat_info("region_m51")



