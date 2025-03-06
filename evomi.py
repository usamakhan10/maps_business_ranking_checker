import requests
from dotenv import load_dotenv
import os

load_dotenv(".env")

PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')
PROXY_URL = "http://core-residential.evomi.com:1000"


PROXY = {
    "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@rp.evomi.com:1000",
    "https": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@rp.evomi.com:1000"
}

def make_request(url):
    response = requests.get(url, proxies=PROXY)
    return response