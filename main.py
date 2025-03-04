from dotenv import load_dotenv
load_dotenv()
import requests
import asyncio
import os
import datetime

import parser
from database.models import async_main, async_session
from database.queries import insert_post, get_post
from sources import VK_PUBLICS_NAMES
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"








#data = get_posts(VK_PUBLICS_NAMES["murmansk"], 10)
#print(data)

async def main():
    await async_main()
    posts = await parser.parse_vk()
    for post in posts:
        time = int(post[3])
        await insert_post(id=int(post[0]),text=post[1],
                        url=post[2],
                        parse_time=datetime.datetime.fromtimestamp((int(post[3]))),
                        group=post[4]
                        )
    #await insert_post("TEXT", "URL", datetime.datetime.now(),"GROUP")


if __name__ == '__main__':

    try:
        asyncio.run(main())
        

    except KeyboardInterrupt:
        print("interrupt")