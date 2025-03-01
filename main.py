from dotenv import load_dotenv
import requests
import os

from sources import VK_PUBLICS

load_dotenv()
domain ="club224630814"
#request = f"https://api.vk.com/method/wall.get?access_token={os.getenv("VK_API_TOKEN")}&v={os.getenv("VK_API_VERSION")}&domain={domain}"

response = requests.get('https://api.vk.com/method/wall.get', 
                        params={
                            'access_token': os.getenv("VK_API_TOKEN"),
                            'v': os.getenv("VK_API_VERSION"),
                            'domain' : domain
                        }
                        )
data = response.json()['response']['items']
print(data)
