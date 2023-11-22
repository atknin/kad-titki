import requests
import os
#!/usr/bin/env python3
import requests
from requests.auth import HTTPProxyAuth
from fake_useragent import UserAgent
from bs4 import BeautifulSoup, element
from datetime import datetime
import itertools
import json
import time
import os,sys
import subprocess
from functions import proxy
from getcaseid import process
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from seleniumbase import Driver

from write import to_excel
ua = UserAgent()
headless = False
driver = Driver(uc=True, incognito=True, proxy=proxy(), agent  = ua.random,headless=headless)
# меняем IP адрес при старте
requests.get('https://changeip.mobileproxy.space/?proxy_key=c9d64935f5f935255181a3ee425e83bd')


comp_input = [i.replace('\n','').strip() for i in open('input.txt').readlines()]

print('Здорово) погнали')
for el in comp_input:
    case_id = 1
    try: 
        process(driver, el,case_id)
        driver.quit()
        time.sleep(2)
        ua = UserAgent()
        driver = Driver(uc=True, incognito=True, proxy=proxy(), agent  = ua.random,headless=headless)
        time.sleep(5)
    except Exception as e:
        print('Блять, ошибка')
        print(f'перезагружаем браузер - это плохо, скорее всего ничего не получится у нас')
        raise e
        driver.quit()
        time.sleep(2)
        ua = UserAgent()
        driver = Driver(uc=True, incognito=True, proxy=proxy_server_full, agent  = ua.random)


# записать все в файл
to_excel(comp_input)
driver.quit()