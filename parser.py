from dotenv import load_dotenv
from sources import VK_PUBLICS_NAMES, VK_PUBLICS_IDS
load_dotenv()
import requests
import os
import json
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
    with open('data.json', 'w') as f:
        json.dump(data,f)
    return data

async def parse_vk(posts = 10):
    vk_posts = []
    for group, domain in VK_PUBLICS_NAMES.items():
        group_posts = await get_posts(domain,posts)
        group_id = list(VK_PUBLICS_NAMES.keys())[list(VK_PUBLICS_NAMES.values()).index(domain)]
        for i in range(posts):
            group_url = f"https://vk.com/{domain}?w=wall-{VK_PUBLICS_IDS[group]}_{str(group_posts[i]['id'])}"
            post_info = [
                str(group_posts[i]["id"]),
                group_posts[i]["text"],
                group_url,
                str(group_posts[i]["date"]),
                group
            ]
            vk_posts.append(post_info)
    return vk_posts

        