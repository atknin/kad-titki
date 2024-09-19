import json
import sys
import time
import os
from functions import write_stat, parse_instances,aggento
ua = aggento()
import platform
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(BASE_DIR + '/data'): os.mkdir(BASE_DIR + '/data')
dir_name = None

def write_output(html, cookies,driver,uid):
    dir_name = '/data/' + uid
    # print('uid write_output',uid)
    dir_path = BASE_DIR + dir_name
    if not os.path.exists(dir_path): os.mkdir(dir_path)
    if not os.path.exists(dir_path + '/instances'): os.mkdir(dir_path + '/instances')
    if not os.path.exists(dir_path + '/sides'): os.mkdir(dir_path + '/sides')
    with open(dir_path + '/content.html', 'w', encoding="utf-8") as f: f.write(html)
    with open(dir_path + '/cookies.json', 'w', encoding="utf-8") as f: f.write(json.dumps(cookies))
    if 'error' in cookies:
        raise e

    try:
        data = parse_instances(html, driver.current_url)
        with open(dir_path + '/page_info.json', 'w', encoding="utf-8") as f: f.write(json.dumps(data))
    except Exception as e:
        print('e parse instance', e)
        raise e
    
    

def process(driver, uid):

    print('start process')
    # time.sleep(5)
    url = 'https://kad.arbitr.ru/Card/{}'.format(uid)
    # driver.get(url)
    print('open browser')
    time.sleep(2)
    html = driver.page_source
    all_cookies = driver.get_cookies()
    cookies_dict = {}
    for cookie in all_cookies:
        cookies_dict[cookie['name']] = cookie['value']
    
    try: write_output(html, cookies_dict,driver,uid)
    except Exception as e: 
        print('e',e)
        raise e

if __name__ == '__main__':
    pass
#     case = sys.argv[1]
#     

#     proxy_server = sys.argv[2].split('/')[0]
#     try: proxy_id = sys.argv[2].split('/')[1]
#     except: proxy_id = -1
    
#     if len(sys.argv) < 4:
#         print('no auth proxy')
#         proxy_auth = None
#     else:
#         proxy_auth = {'login': sys.argv[3], 'password': sys.argv[4]}
#     prox = f'{sys.argv[3]}:{sys.argv[4]}@{proxy_server}'
#     try:

#         driver = Driver(uc=True, incognito=True, proxy=prox, agent=ua.random, headless2=True)
#         result = process(case, proxy=proxy_server, proxy_auth=proxy_auth)
#     except:
#         driver.quit()
#     driver.quit()

# else:
#     driver = Driver(uc=True, incognito=True, proxy=prox,agent = ua.random, headless2=True,)
#     driver.quit()
