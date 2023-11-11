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
from seleniumbase import Driver
import time
from functions import parse_cases_list

ua = UserAgent()
WAIT_BEFORE_READ = 1
import random

# proxy = {'id': 60539, 'ip': 'hproxy.site', 'port': '12371', 'login': 'aS8rUq', 'password': 'abehsUgEsuvN', 'source': 2, 'added_at': '2019-12-15T22:29:01.747Z', 'last_attempt_at': '2020-01-10T09:29:04.635Z', 'is_valid': True, 'valid_index': 0}
proxy = {'id': 60539, 'ip': '192.168.10.35', 'port': '50003', 'login': 'admin', 'password': 'admin', 'source': 2,
         'added_at': '2019-12-15T22:29:01.747Z', 'last_attempt_at': '2020-01-10T09:29:04.635Z', 'is_valid': True,
         'valid_index': 0}

proxy_server = f'http://{proxy["ip"]}:{proxy["port"]}'
proxy_server_full = f'{proxy["login"]}:{proxy["password"]}@{proxy["ip"]}:{proxy["port"]}'

proxy_auth = {'login': f'{proxy["login"]}', 'password': f'{proxy["password"]}'}

# import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECONDS_BEFORE_READ = 0.5
browser = None
result = {}
case = ''
driver = Driver(uc=True, incognito=True, proxy=proxy_server_full, agent=ua.random)


def restart_proxy():
    dir_path = str(BASE_DIR) + '/data/' + str(case_uid) + '/cookies.json'
    os.remove(dir_path)
    session = requests.Session()
    session.headers.update({
                               'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.102011-10-16 20:23:10'})
    resp = session.get(
        'http://192.168.10.35:8000/api/devices/modem/reconnect?token=0b1d2c1c3f0f31da36f8d33e45aff964d7157bad&id=5')
    print('proxy restart')
    time.sleep(10)


class LoadHandler(object):
    def __init__(self, search_phrase, proxy_auth=None):
        self.search_phrase = search_phrase
        self.proxy_auth = proxy_auth

    def GetAuthCredentials(self, browser, frame, is_proxy, host, port, realm, scheme, callback):
        if is_proxy:
            callback.Continue(self.proxy_auth['login'], self.proxy_auth['password'])
            return True
        return False

    def OnLoadingStateChange(self, browser, is_loading, **kwargs):
        print('onload')

        def close_after_time(html):
            print('closeafter')
            global dir_name
            global browser
            global BASE_DIR
            cookies = {'error': 'closed after time'}
            print(cookies)
            browser.CloseBrowser()
            browser = None
            cef.Shutdown()

        def close_after_time_js():
            print('closeaftejsr')
            global browser
            global BASE_DIR
            JS_CODE = open(BASE_DIR + '/close_after_time_js.js').read()
            if browser:
                browser.ExecuteJavascript(JS_CODE)

        if not is_loading and browser is not None:
            print("loading completed")
            print(browser.GetUrl())  # should be redirected to https://www.google.com
            bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)

            def callback(data):
                return back_to_python(self.search_phrase, data)

            def close_after_time(data):
                return back_to_python(self.search_phrase, {'not': 1})

            bindings.SetFunction("close_after_time", close_after_time)
            threading.Timer(WAIT_BEFORE_READ, close_after_time_js).start()
            bindings.SetFunction("back_to_python", callback)
            browser.SetJavascriptBindings(bindings)
            t = threading.Timer(SECONDS_BEFORE_READ, runjs)
            t.start()
        elif browser is not None:

            print("loading completed")
            print(browser.GetUrl())  # should be redirected to https://www.google.com
            bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)

            def close_after_time(data):
                return back_to_python(self.search_phrase, {'not': 1})

            bindings.SetFunction("close_after_time", close_after_time)
            threading.Timer(WAIT_BEFORE_READ, close_after_time_js).start()
            browser.SetJavascriptBindings(bindings)
            t = threading.Timer(SECONDS_BEFORE_READ, runjs)
            t.start()
        else:
            print("loading not yet completed")


def back_to_python(search_phrase, data):
    global browser
    global result
    result = data

    if 'not' in data:
        restart_proxy()
    else:
        browser.CloseBrowser()
        browser = None
    return data


def runjs():
    global browser
    global case
    JS_CODE = open(BASE_DIR + '\search_kad_arbitr.js').read().replace('[case_number]', case)
    
    driver.execute_script(JS_CODE)
    
        #driver.quit()
        #raise Exception


def process(case_number, case_id):
    global browser
    global case
    global result
    case = case_number

    driver.get("http://kad.arbitr.ru")
    time.sleep(2)
    #try:
    runjs()
    #except Exception:
    #   return {}
    time.sleep(2)
    html = driver.page_source
    data = parse_cases_list(html)

    # check_versions()
    # sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    # switches = {
    #     "enable-media-stream": "",
    #     "proxy-server": proxy,
    #     "disable-gpu": "",
    # }
    # cef.Initialize(switches=switches,settings={
    #     "user_agent":ua.random
    #     })
    # browser = cef.CreateBrowserSync()
    # browser.SetClientHandler(LoadHandler(case, proxy_auth=proxy_auth))
    # browser.LoadUrl('http://kad.arbitr.ru')
    # cef.MessageLoop()

    # # Writing to sample.json
    # with open("sample.json", "w") as outfile:
    #    outfile.write(result)
    if len(data) == 0:
        return
    arr = {'row': data[0]}
    url_update = 'http://app.legaltrack.ru/kad/write_update_short/{}/'.format(case_id)
    resp = requests.post(url_update, json=arr)
    print('resp?', resp)

    if resp.status_code == 200:
        print('data send')
    else:
        with open("error.html", "w") as outfile:
            outfile.write(resp.text)

    return result


def check_versions():
    ver = cef.GetVersion()
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"


# save_log('Start script')
#case = sys.argv[1]
#case_id = sys.argv[2]
# proxy_server = sys.argv[2]193.8.1.201:6738/319377
# proxy_auth = {'login':sys.argv[3],'password':sys.argv[4]}
#result = process(case, case_id)

#driver.quit()
# 
# def main():
# 
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 
#     while True:
#         starts = requests.get('http://app.legaltrack.ru/kad/get_case_for_update_tmp/').json()
#         print(starts)
#         if 'cases' not in starts:
#             print('sleep 127')
#             time.sleep(30)
#             continue
#         if len(starts['cases']) == 0:
#             print('sleep')
#             time.sleep(30)
#             continue
# 
#         for start in starts['cases']:
#             case = start['number']  # 'А40-191296/2019'
#             case_id = start['id']
#             print(sys.executable, BASE_DIR + "/getcaseid.py", case, case_id)
#             cmd = [sys.executable, BASE_DIR + "/getcaseid.py", case, str(case_id)]
#             timeout = 30
#             try:
#                 result = process(case, case_id)
#                 # process = subprocess.Popen(
#                 #     cmd,
#                 #     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                 # )
#                 # out, err = process.communicate(timeout=timeout)
# 
# 
#             except subprocess.TimeoutExpired:
#                 arr = {'row': {'not': 1}}
#                 url_update = 'http://app.legaltrack.ru/kad/write_update_short/{}/'.format(case_id)
#                 resp = requests.post(url_update, json=arr)
#                 print(f'Timeout for ({timeout}s) expired')
#                 process.kill()
# 

if __name__=='__main__':
     
    result = process('М-694/2023', '173982')
    driver.quit()