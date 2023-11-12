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
from getcaseid import process
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from seleniumbase import Driver
proxy = {'ip': 'wproxy.site', 'port': '11996', 'login': 'PywyMF', 'password': 'uKgYE8eH3am2', 'source': 2, 'added_at': '2019-12-15T22:29:01.747Z', 'last_attempt_at': '2020-01-10T09:29:04.635Z', 'is_valid': True, 'valid_index': 0}
proxy_server = f'http://{proxy["ip"]}:{proxy["port"]}'
proxy_server_full = f'{proxy["login"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
proxy_auth = {'login':f'{proxy["login"]}','password':f'{proxy["password"]}'}
from write import to_excel
ua = UserAgent()
driver = Driver(uc=True, incognito=True, proxy=proxy_server_full, agent  = ua.random)#,headless=True)
# меняем IP адрес при старте
requests.get('https://changeip.mobileproxy.space/?proxy_key=c9d64935f5f935255181a3ee425e83bd')


comp_input = [i.replace('\n','').strip() for i in open('input.txt').readlines()]


for el in comp_input:
    print('Начинаем', el)
    case_id = 1
    print(sys.executable, BASE_DIR+"/getcaseid.py",el,case_id)
    try: 
        process(driver, el,case_id)
        time.sleep(5)
    except Exception as e:
        raise e
        print('ошибка')
        print(f'перезагружаем браузер')
        driver.quit()
        time.sleep(2)
        ua = UserAgent()
        driver = Driver(uc=True, incognito=True, proxy=proxy_server_full, agent  = ua.random)


# записать все в файл
to_excel(comp_input)
driver.quit()