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


proxy = {'id': 60539, 'ip': 'wproxy.site', 'port': '16691', 'login': 'fey8Me', 'password': 'yVcexzYVaDTU', 'source': 2, 'added_at': '2019-12-15T22:29:01.747Z', 'last_attempt_at': '2020-01-10T09:29:04.635Z', 'is_valid': True, 'valid_index': 0}
proxy_server = f'http://{proxy["ip"]}:{proxy["port"]}'
proxy_server_full = f'{proxy["login"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'
proxy_auth = {'login':f'{proxy["login"]}','password':f'{proxy["password"]}'}

ua = UserAgent()
driver = Driver(uc=True, incognito=True, proxy=proxy_server_full, agent  = ua.random)#,headless=True)

while True:
    try:
        starts = requests.get('http://app.legaltrack.ru/kad/get_case_for_update_tmp/').json()
    except: 
        time.sleep(40)
        continue
    print(starts)
    if 'cases' not in starts:
        time.sleep(3)
        continue
    if len( starts['cases']) ==0: 
        print('sleep')
        time.sleep(40)
        continue

    for start in starts['cases']:
        case =start['number']# 'А40-191296/2019'
        case_id = start['id']
        print(sys.executable, BASE_DIR+"/getcaseid.py",case,case_id)
        try: 
            process(driver, case,case_id)
            time.sleep(5)
        except:
            arr = {'row':{'not':1}}
            url_update = 'http://app.legaltrack.ru/kad/write_update_short/{}/'.format(case_id)
            resp = requests.post(url_update, json = arr)
            print(f'перезагружаем браузер')
            driver.quit()
            time.sleep(2)
            ua = UserAgent()
            driver = Driver(uc=True, incognito=True, proxy=proxy_server_full, agent  = ua.random)



        

