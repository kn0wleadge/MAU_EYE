from dotenv import load_dotenv
load_dotenv()
import requests
import asyncio
import os
import datetime

from database.models import async_main
from database.models import async_session
from database.models import insert_post
from sources import VK_PUBLICS
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"






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
    await insert_post("TEXT", "URL", datetime.datetime.now(),"GROUP")


if __name__ == '__main__':

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("interrupt")