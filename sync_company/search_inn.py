#!/usr/bin/env python3

import json
import platform
import sys
import time
import threading
from functools import partial
import os
import requests
from bs4 import BeautifulSoup
from cefpython3 import cefpython as cef
from datetime import datetime, timedelta
# import subprocess
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from fake_useragent import UserAgent
import json
from fake_useragent import UserAgent

ua = UserAgent()
SECONDS_BEFORE_READ = 0.5
browser = None
result = {}
case = ''
date_from = ''




class LoadHandler(object):
    def __init__(self, search_phrase, proxy_auth=[None, None]):
        self.search_phrase = search_phrase
        self.proxy = proxy_auth[0]
        self.proxy_auth = proxy_auth[1]

    def GetAuthCredentials(self, browser, frame, is_proxy, host, port, realm, scheme, callback):
        if is_proxy:
            callback.Continue(self.proxy_auth['login'], self.proxy_auth['password'])
            return True
        return False

    def OnLoadingStateChange(self, browser, is_loading, **kwargs):
        if not is_loading and browser is not None:
            # print("loading completed")
            # print(browser.GetUrl()) # should be redirected to https://www.google.com
            bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=False)

            def callback(data, cookie):
                return back_to_python(self.proxy, self.proxy_auth, data, cookie)

            bindings.SetFunction("back_to_python", callback)
            browser.SetJavascriptBindings(bindings)
            t = threading.Timer(SECONDS_BEFORE_READ, runjs)
            t.start()
        else:
            pass
            # print("loading not yet completed")


def format_proxy(proxy, proxy_auth):
    if proxy_auth is not None:
        return {'http': 'http://{}:{}@{}'.format(proxy_auth['login'], proxy_auth['password'], proxy),
                'https': 'https://{}:{}@{}'.format(proxy_auth['login'], proxy_auth['password'], proxy)}
    else:
        return {'http': 'http://{}:{}'.format(proxy['ip'], proxy['port']),
                'https': 'https://{}:{}'.format(proxy['ip'], proxy['port'])}


def get_headers():
    headers = {
        'User-Agent': ua.random,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Host': 'kad.arbitr.ru',
        'Referer': 'http://kad.arbitr.ru/',
        'x-date-format': 'iso',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return headers


def get_text(parent):
    return ''.join(parent.find_all(text=True, recursive=False)).strip()


def parse_company(content):
    soup = BeautifulSoup(content.decode('utf-8'), 'html.parser')
    cases = []
    case_trs = soup.find_all('tr')
    for case_tr in case_trs:
        case = {}
        case_td = case_tr.find('td', attrs={'class': 'num'})
        court_td = case_tr.find('td', attrs={'class': 'court'})

        judge_div = court_td.find('div', attrs={'class': 'judge'})
        court_div = court_td.find('div', attrs={'class': ''})

        sides_1_td = case_tr.find('td', attrs={'class': 'plaintiff'})
        sides_2_td = case_tr.find('td', attrs={'class': 'respondent'})

        num_case_a = case_td.find('a')
        # date_span = case_td.find('span')

        # case['date'] = datetime.strptime(
        #     date_span.text.strip(), '%d.%m.%Y'
        # )
        case['case'] = num_case_a.text.strip()
        case['uid'] = num_case_a['href'].split('/')[-1].strip()
        if judge_div:
            case['judge'] = judge_div.text.strip()
        else:
            case['judge'] = None
        if court_div:
            case['court'] = court_div.text.strip()
        else:
            case['court'] = None
        case['hearingDate'] = case_td.find('span').text.strip()
        try:
            case['istec'] = sides_1_td.find('span', attrs={'class': 'js-rollover b-newRollover'}).text.strip()
        except:
            case['istec'] = ''
        try:
            case['istec-details'] = sides_1_td.find('span', attrs={'class': 'js-rolloverHtml'}).text.strip()
        except:
            case['istec-details'] = ''
        try:
            case['otvetchik'] = sides_2_td.find('span', attrs={'class': 'js-rollover b-newRollover'}).text.strip()
        except:
            case['otvetchik'] = ''
        try:
            case['otvetchik-details'] = sides_2_td.find('span', attrs={'class': 'js-rolloverHtml'}).text.strip()
        except:
            case['otvetchik-details'] = ''
        cases.append(case)
    return cases


def get_all_pages(data, cookie, proxy, proxy_auth):
    global case
    global result
    global date_from
    if not data['pages']: return result
    try:
        for page in range(2, int(data['pages']) + 1):
            proxies = format_proxy(proxy, proxy_auth)
            data_sent = {"Page": page, "Count": 25, "Courts": [], "DateFrom": date_from, "DateTo": '',
                        "Sides": [{"Name": case, "Type": -1, "ExactMatch": False}], "Judges": [], "CaseNumbers": [],
                        "WithVKSInstances": False}
            resp = requests.post('http://kad.arbitr.ru/Kad/SearchInstances', proxies=proxies, headers=get_headers(),
                                data=json.dumps(data_sent), cookies=cookie)
            data['items'] += parse_company(resp.content)
    except:
        print('cannot get second+ pages')
    result = data['items']
    return result
    # print(result,len(result))


def back_to_python(proxy, proxy_auth, data, cookie):
    global browser
    global result
    print('back_to_python')
    if 'pages' in data:
        result = get_all_pages(data, cookie, proxy, proxy_auth)
    else:
        result = {'error': 'not found inn/ogrn or kad.arbitr.ru error'}
    try:
            
        browser.CloseBrowser()
        browser = None
    except: pass
    return result


def runjs():
    global browser
    global case
    global date_from

    # print('*** run JS')
    # print(case,date_from)
    JS_CODE = open(BASE_DIR + '/search_kad_arbitr.js').read().replace('[inn_ogrn]', case).replace('[date_from]',date_from)
    if browser is not None: browser.ExecuteJavascript(JS_CODE)
    # print('*** JS should call Python function in a while')


def process(case_number, proxy=None, proxy_auth=None):
    global browser
    global case
    global result
    case = case_number
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    switches = {
        "enable-media-stream": "",
        "proxy-server": proxy,
        "disable-gpu": "",
    }
    settings = {
        "windowless_rendering_enabled": True,
        "user_agent": ua.random
    }
    cef.Initialize(switches=switches, settings=settings)
    browser = cef.CreateBrowserSync()
    browser.SetClientHandler(LoadHandler(case, proxy_auth=[proxy, proxy_auth]))
    browser.LoadUrl('http://kad.arbitr.ru')
    cef.MessageLoop()


    arr = {'cases':result, 'inn':case_number}
    print('data to send',arr)

    url_update = 'http://app.legaltrack.ru/api/v4/company/update-inn'

    resp = requests.post(url_update, json = arr)

    if resp.status_code == 200:
        print('data send')
    else:
        with open("error.html", "w", encoding='utf-8') as outfile:
            outfile.write(resp.text)

    cef.Shutdown()
    return result


def check_versions():
    ver = cef.GetVersion()
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"




case = sys.argv[1]
try:
    is_synced = int(sys.argv[2])
except: is_synced = 0
if is_synced == 0: 
    date_from = '01.01.1900'
else: 
    # today minus 15 days from now
    date_from = (datetime.now() - timedelta(days=60)).strftime('%d.%m.%Y')

proxy = {'id': 60539, 'ip': 'hproxy.site', 'port': '12371', 'login': 'aS8rUq', 'password': 'abehsUgEsuvN', 'source': 2, 'added_at': '2019-12-15T22:29:01.747Z', 'last_attempt_at': '2020-01-10T09:29:04.635Z', 'is_valid': True, 'valid_index': 0}
proxy_server = f'http://{proxy["ip"]}:{proxy["port"]}'
proxy_auth = {'login':f'{proxy["login"]}','password':f'{proxy["password"]}'}

try:
    result = process(case, proxy=proxy_server, proxy_auth=proxy_auth)
except Exception as e:
    raise e
print(json.dumps(result))
