from dotenv import load_dotenv
load_dotenv()
import requests
import os
import asyncio
import json
import logging
import datetime
class VkParser():
    def __init__(self, token):
        api_token:str

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
async def get_groupid(domain):
    response = requests.get('https://api.vk.com/method/groups.getById',
                            params = {
                                'access_token': os.getenv("VK_API_TOKEN"),
                                'v': os.getenv("VK_API_VERSION"),
                                'group_id' : domain
                            })
    return response['response']['groups'][0]['id']
def add_test_negative_posts():
    return([{
                "id" : 15,
                "text" : os.getenv("TEST_POST1_TEXT"),
                "post_url" : "https://vk.com/wall-184888396_23930",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "group_name" : "Gorod51",
                "parse_date" : str(int(datetime.datetime.now().timestamp()))    
            },
            {
                "id" : 16,
                "text" : os.getenv("TEST_POST2_TEXT"),
                "post_url" : "https://vk.com/wall-59208578_578017",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 10:15:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "group_name" : "SeverPost",
                "parse_date" : str(int(datetime.datetime.now().timestamp()))    
            },
            {
                "id" : 17,
                "text" : os.getenv("TEST_POST3_TEXT"),
                "post_url" : "https://murmansk.mk.ru/incident/2024/08/28/ugolovnoe-delo-po-faktu-vzyatki-v-universitete-vozbudili-v-murmanske.html",
                "post_date" : str(int(datetime.datetime.strptime("2024.08.28 09:22:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "group_name" : "SeverPost",
                "parse_date" : str(int(datetime.datetime.now().timestamp()))    
            }
            ])

async def parse_vk(posts, sources:list):
    parse_date = str(int(datetime.datetime.now().timestamp()))
    vk_posts = []
    for source in sources:
        group_posts = await get_posts(sources["domain"],posts)
        group_posts = await get_posts(domain,posts)
        for i in range(posts):
            post_url = f"https://vk.com/{sources['domain']}?w=wall-{sources['id']}_{str(group_posts[i]['id'])}"
            post_info = {
                "id" : str(group_posts[i]["id"]),
                "text" : group_posts[i]["text"],
                "post_url" : post_url,
                "post_date" : str(group_posts[i]["date"]),
                "group_name" : group,
                "parse_date" : parse_date
            }
            vk_posts.append(post_info)
            logging.info(f"Parsed post with url - {post_url}")
        
    for group, domain in VK_PUBLICS_NAMES.items():
        group_posts = await get_posts(domain,posts)
        for i in range(posts):
            post_url = f"https://vk.com/{domain}?w=wall-{VK_PUBLICS_IDS[group]}_{str(group_posts[i]['id'])}"
            post_info = {
                "id" : str(group_posts[i]["id"]),
                "text" : group_posts[i]["text"],
                "post_url" : post_url,
                "post_date" : str(group_posts[i]["date"]),
                "group_name" : group,
                "parse_date" : parse_date
            }
            vk_posts.append(post_info)
            logging.info(f"Parsed post with url - {post_url}")
    test_posts = add_test_negative_posts()
    for post in test_posts:
        logging.info(f"TEST POST parsed url - {post['post_url']}")
        vk_posts.append(post)
    return vk_posts

if __name__ == '__main__':
    asyncio.run(parse_vk())

