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
from fake_useragent import UserAgent

import time
from functions import parse_cases_list,da_data
import random
import os

# import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))



def runjs(driver,inn_ogrn):
    JS_CODE = open(BASE_DIR+'/search_kad_arbitr.js').read().replace('[inn_ogrn]',inn_ogrn).replace('[court_name]','АС города Москвы')
    driver.execute_script(JS_CODE)

def process(driver, inn_ogrn,case_id):
    
    driver.get("https://kad.arbitr.ru")
    time.sleep(3)
    runjs(driver,inn_ogrn)
    time.sleep(2)
    html = driver.page_source
    data = parse_cases_list(html) 


    # Check whether the specified path exists or not
    path = f"data/{inn_ogrn}"
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print("The new directory is created!")
    


    # пройтись по всем делам и сохранить информацию
    for res in data:
        path_f = f'{path}/{res.get("uid")}.json'
        if not os.path.isfile(path):
            json_object = json.dumps(res, indent=4)
            # Writing to sample.json
            with open(path_f, "w") as outfile:
                outfile.write(json_object)
        
        # добавляем дадату        
        with open(path_f) as f:
            body = json.loads(f.read())
            if ('dadata-otvetchik' not in body) and (body.get('otvetchik-inn') is not None):
                print('download DADATA')
                json_object = json.dumps(da_data(body), indent=4)
                with open(path_f, "w") as outfile:
                    outfile.write(json_object)
            else:
                print('уже было скачано')
    return driver