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
from write import doxl
import time
from functions import parse_cases_list
import random


# import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))



def runjs(driver,case_number):
    JS_CODE = open(BASE_DIR+'/search_kad_arbitr.js').read().replace('[inn_ogrn]',case_number)
    driver.execute_script(JS_CODE)

def process(driver, case_number,case_id):
    
    driver.get("https://kad.arbitr.ru")
    time.sleep(3)
    runjs(driver,case_number)
    time.sleep(2)
    html = driver.page_source
    data = parse_cases_list(html) 
    
    print([i for i in data])
    doxl(data,case_number)
 
    return driver