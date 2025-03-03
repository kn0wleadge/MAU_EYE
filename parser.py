from dotenv import load_dotenv
from sources import VK_PUBLICS
load_dotenv()
import requests
import os
async def get_posts(domain, count):

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

async def parse_vk():
    vk_posts = []
    for group in VK_PUBLICS:
        group_posts = get_posts(group,10)
        