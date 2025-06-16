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
    return([#{
    #             "pid" : 15,
    #             "text" : "Этот университет ужасен!!!Хуже общежития, чем в МАУ - я не видел, там ползают тараканы, а еще меня оскорбил охранник!",
    #             "post_url" : "https://vk.com/wall-184888396_23930",
    #             "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
    #             "sid" : 181923765,
    #             "parse_date" : str(int(datetime.datetime.now().timestamp())),
    #             "likes" : 100,
    #             "views" : 10000000,
    #             "comments" : 50,
    #             "reposts" : 30
                  
    #         },
            {
               "pid" : 16,
                "text" : "Двоих студентов журфака МАУ отчислили и пятерым объявили выговор из-за «недопустимого поведения в публичном пространстве», сообщил РБК пресс-секретарь факультета Андрей Кленин",
                "post_url" : "https://vk.com/wall-25232578_12924287",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "sid" : 181923765,
                "parse_date" : str(int(datetime.datetime.now().timestamp())),
                "likes" : 0,
                "views" : 0,
                "comments" : 0,
                "reposts" : 0 
            },
            {
               "pid" : 17,
                "text" : "Ведущему ученому химико-биологического кластера при МАУ предъявлено хищение 20 млн рублей при исследовании лекарства для онкобольных. Уголовное дело касается сложной вакцины и обычных мышей. Подробности стали известны «Фонтанке» 12 сентября.",
                "post_url" : "https://www.fontanka.ru/2024/09/12/74078726/",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "sid" : 181923765,
                "parse_date" : str(int(datetime.datetime.now().timestamp())),
                "likes" : 0,
                "views" : 0,
                "comments" : 0,
                "reposts" : 0 
            },
            {
               "pid" : 18,
                "text" : "Не так давно на должность проректора по организационно-хозяйственной работе был назначен человек с выдающимися управленческими качествами - Станислав Сергеевич Владимиров, имеющий судимость за самоуправство в 1996 году в Краснодарском крае.Возникают вопросы к службе безопастности МАУ, каким образом человек имеющий пятно в своей биографии прошел проверку и был с легкостью допущен к работе, предполагающую в том числе и работу со студентами.ВЧК-ОГПУ поинтересовался у коллег нового проректора его управленческими качествами, и, сходу, выяснил следующее: Владимиров С. С., в связке с другими высокопоставленными сотрудниками университета, действует в интересах ряда коммерческих структур. Действует с целью личного обогащения, но во вред серьезной научно-образовательной организации с авторитетом как в России, так и за ее пределами.",
                "post_url" : "https://glvk.net/articles/204016-v_cankt-peterburgskom_politehnicheskom_universitete_petra_velikogo_zreet_novyj_skandal",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "sid" : 181923765,
                "parse_date" : str(int(datetime.datetime.now().timestamp())),
                "likes" : 0,
                "views" : 0,
                "comments" : 0,
                "reposts" : 0 
            },
            {
               "pid" : 19,
                "text" : "В МАУ скандал из-за «каталога первокурсниц» с сексистскими оскорблениями.По университетским чатам разошелся список первокурсниц, в котором были личные данные поступивших в вуз и сексистские оценки от неких «судей».",
                "post_url" : "https://moskvichmag.ru/gorod/v-baumanke-skandal-iz-za-kataloga-pervokursnits-s-seksistskimi-oskorbleniyami/",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "sid" : 181923765,
                "parse_date" : str(int(datetime.datetime.now().timestamp())),
                "likes" : 0,
                "views" : 0,
                "comments" : 0,
                "reposts" : 0 
            },
            {
               "pid" : 20,
                "text" : "  ",
                "post_url" : "https://regions.ru/mytischi/proisshestviya/chetveryh-prepodavateley-filiala-baumanki-v-podmoskove-poymali-na-vzyatkah",
                "post_date" : str(int(datetime.datetime.strptime("2022.06.24 11:18:00", '%Y.%m.%d %H:%M:%S').timestamp())),
                "sid" : 181923765,
                "parse_date" : str(int(datetime.datetime.now().timestamp())),
                "likes" : 0,
                "views" : 0,
                "comments" : 0,
                "reposts" : 0 
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

