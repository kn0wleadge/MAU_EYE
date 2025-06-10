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
def get_group_data(domain):
    response = requests.get('https://api.vk.com/method/groups.getById',
                            params = {
                                'access_token': os.getenv("VK_API_TOKEN"),
                                'v': os.getenv("VK_API_VERSION"),
                                'group_id' : domain
                            })
    #print(response.text)
    result = {"id": int(response.json()['response']['groups'][0]['id']),
              "name": response.json()['response']['groups'][0]['name']}
    return result
def add_test_negative_posts():
    return([{
                "pid" : 15,
                "text" : "Этот университет ужасен!!!Хуже общежития, чем в МАУ - я не видел, там ползают тараканы, а еще меня оскорбил охранник!",
                "post_url" : "https://vk.com/wall-184888396_23930",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "sid" : 181923765,
                "parse_date" : str(int(datetime.datetime.now().timestamp())),
                "likes" : 100,
                "views" : 10000000,
                "comments" : 50,
                "reposts" : 30
                  
            }
            ])

async def parse_vk(posts, sources:list):
    parse_date = str(int(datetime.datetime.now().timestamp()))
    vk_posts = []
    for source in sources:
        group_posts = await get_posts(source["sdomain"],posts)
        for i in range(posts):
            
            post_url = f"https://vk.com/{source['sdomain']}?w=wall-{source['sid']}_{str(group_posts[i]['id'])}"
            #print(group_posts[i])
            post_info = {
                "pid" : group_posts[i]["id"],
                "text" : group_posts[i]["text"],
                "post_url" : post_url,
                "post_date" : str(group_posts[i]["date"]),
                "sid" : source['sid'],
                "parse_date" : parse_date,
                "likes" : group_posts[i]["likes"]["count"],
                "views" : group_posts[i]["views"]["count"],
                "comments" : group_posts[i]["comments"]["count"],
                "reposts" : group_posts[i]["reposts"]["count"]
            }
            vk_posts.append(post_info)
            print(f"Parsed post with url - {post_url}")
        
    test_posts = add_test_negative_posts()
    for post in test_posts:
        print(f"TEST POST parsed url - {post['post_url']}")
        vk_posts.append(post)
    #print(f"vk_posts - {vk_posts}")
    return vk_posts

if __name__ == '__main__':
    #asyncio.run(parse_vk())
    print(get_group_id("reginfo51"))

