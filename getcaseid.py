import json
import platform
import sys
import time
import threading
from functools import partial
import os 
import requests
from bs4 import BeautifulSoup
import random 
from cefpython3 import cefpython as cef
from fake_useragent import UserAgent

import time
from functions import parse_cases_list
import random


# import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))



def runjs(driver,case_number):
    JS_CODE = open(BASE_DIR+'/search_kad_arbitr.js').read().replace('[case_number]',case_number)
    driver.execute_script(JS_CODE)

def process(driver, case_number,case_id):
    
    driver.get("https://kad.arbitr.ru")
    time.sleep(3)
    runjs(driver,case_number)
    time.sleep(2)
    html = driver.page_source
    data = parse_cases_list(html) 

    if len(data) == 0: 
        print('ноль рузельтатов')
        arr = {'row':{'not': 1}}
        url_update = 'http://app.legaltrack.ru/kad/write_update_short/{}/'.format(case_id)
        resp = requests.post(url_update, json = arr)
        raise 1

    arr = {'row':data[0]}
    url_update = 'http://app.legaltrack.ru/kad/write_update_short/{}/'.format(case_id)
    resp = requests.post(url_update, json = arr)

    print('resp?',resp)

    if resp.status_code == 200: print('data send')
    else:
        with open("error.html", "w") as outfile:
            outfile.write(resp.text)
        raise 1
    
    return driver