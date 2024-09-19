import requests
import os
#!/usr/bin/env python3
import requests
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup, element
from datetime import datetime
import itertools
import json
import time
import os,sys
import subprocess
from functions import proxy, cach_inn,proxy_key,aggento
from getcaseid import process
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from seleniumbase import Driver

from write import to_excel
ua = aggento()

print(proxy())
headless = False
driver = Driver(uc=True, incognito=True, proxy=proxy(), agent  = ua,headless=headless)
# меняем IP адрес при старте
 
# proxy_req = requests.get(f'https://changeip.mobileproxy.space/?proxy_key={proxy_key}')
# print('proxy_req',proxy_key,proxy_req.text)


# comp_input = [i.replace('\n','').strip() for i in open('input.txt').readlines()]
comp_input = [i.get('inn') for i in requests.get('https://roma.kazna.tech/api/get-companies').json().get('data')]
# нужно прогнать excel на ответчиков, записать те инн которых нет 
# try: cach_inn()
# except: pass

print('Работаем с компаниями:')
for el in comp_input:
    case_id = 1
    try: 
        process(driver, el,case_id)
        driver.quit()
        time.sleep(2)
        ua = aggento()
        driver = Driver(uc=True, incognito=True, proxy=proxy(), agent  = ua,headless=headless)
        time.sleep(5)
    except Exception as e:
        print('ошибка...')
        print(f'перезагружаем браузер')
        # raise e
        driver.quit()
        time.sleep(2)
        ua = aggento()
        driver = Driver(uc=True, incognito=True, proxy=proxy(), agent  = ua)


# записать все в файл
# to_excel(comp_input)
# driver.quit()