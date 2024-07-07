import os
import requests 
import json 
from bs4 import BeautifulSoup, element
from datetime import datetime
import itertools
from fake_useragent import UserAgent
import configparser
import random
stat_base_url = 'http://app.legaltrack.ru'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(BASE_DIR, 'data')
config = configparser.ConfigParser()
config.read('config.ini')

if not os.path.isdir(data_path):  os.mkdir(data_path)
proxy_key = config.get('Proxy', 'key')

def token_dadata():
    a = [config.get('Dadata', 'token1'),config.get('Dadata', 'token2')]
    return random.choice(a)

def proxy(dictionary = False):
    login = config.get('Proxy', 'login')
    password = config.get('Proxy', 'password')
    ip = config.get('Proxy', 'ip')
    port = config.get('Proxy', 'port')

    proxy_server_full = f'{login}:{password}@{ip}:{port}'

    if dictionary:
        return  {   "http"  : f'http://{proxy_server_full}', 
                     "https" :f'https://{proxy_server_full}',   
                }
    else:
        return proxy_server_full

def stripped_text(tag):
    return getattr(tag, 'text').strip()

def read_sides_column(soup, name):
    table = soup.find('table', {'class': 'b-case-info'})
    rows = table.find_all('td', {'class': name})
    batches = [r.find_all('a') for r in rows]
    data_rows = itertools.chain(*batches)
    sides = list(map(stripped_text, data_rows))
    formatted = ', '.join(sides)
    return formatted

def transform_date(string):
    # 26 июля 2017
    numerical = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
        'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ]
    day, month, year = string.split(' ')
    month = numerical.index(month) + 1
    date = datetime(year=int(year), month=int(month), day=int(day))
    return date.strftime('%Y-%m-%d %H:%M:%S')

def write_stat(id_proxy,data):
    print('[.] stat')
    url_stat = stat_base_url + '/api/report_attempt_result/{}/'.format(id_proxy)
    keys = ['url','who','data','method',
        'headers','is_succeed','case_uid',
        'response_time','response_body',
        'response_code','response_error',
        'request_method','block_this']
    sent_data = {}
    for key in keys:
        if key in data: sent_data[key] = data[key]
        else: sent_data[key] = 0
    return 0# requests.post(url_stat,data = json.dumps(sent_data), proxies = myproxy)


def parse_cases_list(content):
    data = []
    soup = BeautifulSoup(content, 'html.parser')
    case_table = soup.find("div",{'class':'b-cases_wrapper'})
    my_cases = case_table.find_all('tr')
    for line in my_cases:
        element = {}
        element['uid'] = line.find('a')['href'].split('/')[-1]
        element['case'] = line.find('a').text.strip()
                  
        
        court = line.find("td",{'class':'court'}).find_all('div')
        element['court'] = court[2]['title'] if len(court)==3 else court[1]['title']
        
        element['type'] = 'non'

        element['hearingDate'] = line.find("div",{'class':'civil'})['title'] if line.find("div",{'class':'civil'})  else None
        if element['hearingDate'] is not None: element['type'] = 'civil'

        if element['hearingDate'] is None:
            element['hearingDate'] = line.find("div",{'class':'civil_simple'})['title'] if line.find("div",{'class':'civil_simple'})  else None
            if element['hearingDate'] is not None: element['type'] = 'civil_simple'
        
        if element['hearingDate'] is None:
            element['hearingDate'] = line.find("div",{'class':'bankruptcy'})['title'] if line.find("div",{'class':'bankruptcy'})  else None
            if element['hearingDate'] is not None: element['type'] = 'bankruptcy'
        
        if element['hearingDate'] is None:
            element['hearingDate'] = line.find("div",{'class':'default'})['title'] if line.find("div",{'class':'default'})  else None
            if element['hearingDate'] is not None: element['type'] = 'default'


        element['judge'] = line.find("div",{'class':'judge'})['title'] if line.find("div",{'class':'judge'}) else None
    
        istec = line.find("td",{'class':'plaintiff'}).find("span",{'class':'js-rolloverHtml'})
        element['istec'] =  istec.find('strong').text if istec else None
        element['istec-details'] =  istec.text.strip().replace('\t','').replace('\r','').replace('\n',' ').strip() if istec else None
        div_inn = istec.find('div') if istec else None
        element['istec-inn'] =  div_inn.text.replace('\t','').replace('\r','').replace('\n',' ').strip().split(':')[1] if div_inn else None

        otvetchik = line.find("td",{'class':'respondent'}).find("span",{'class':'js-rolloverHtml'})
        element['otvetchik'] =  otvetchik.find('strong').text if otvetchik else None
        element['otvetchik-details'] =  otvetchik.text.strip().replace('\t','').replace('\r','').replace('\n',' ').replace('  ',' ') if otvetchik else None
        div_inn = otvetchik.find('div') if otvetchik else None
        element['otvetchik-inn'] = div_inn.text.replace('\t','').replace('\r','').replace(' ','').replace('\n','').strip().split(':')[1] if div_inn else None
        data.append(element)
    return data

def parse_instances(content,card_link):
    data = {}
    soup = BeautifulSoup(content, 'html.parser')
    try:
        data['case-number'] = soup.find('span', {
                'class': "js-case-header-case_num",
                'data-instance_level': "1"
            }).text.strip()
        data['card-link'] = card_link
        data['case-dur'] = soup.find('li', {'class': "case-dur"}).text.strip() 
        data['case-date'] = soup.find('li', {'class': "case-date"}).text.strip()
        data['type'] = soup.find('h4', {'class': "b-main-info-title"}).text.strip()
        header = soup.find('dt', {'class': "b-iblock__header b-iblock__header_card"}).find('span')
        data['kind'] = ''.join([t for t in header.contents if type(t)==element.NavigableString]).strip()
        data['started-date'] = transform_date(soup.find('li', {'class': "case-date"}).text.strip())
        data['plaintiffs'] = read_sides_column(soup, 'plaintiffs')
        data['defendants'] = read_sides_column(soup, 'defendants')
        data['third'] = read_sides_column(soup, 'third')
        data['others'] = read_sides_column(soup, 'others')
        data['courts'] = ', '.join(set(map(stripped_text, soup.find_all('span', {'class':"instantion-name"}))))
        try:
            data['case-calendar-link'] = soup.find('li', {'class':"case-date"}).find('a')['href']
        except Exception:
            data['case-calendar-link'] = None
    except Exception as e:
        raise e
    instances_html = soup.findAll('div',{'class':"b-chrono-item-header"})
    data['instances'] = []
    for inst in instances_html:
        data['instances'].append({
            'data-court':inst['data-court'],
            'data-id':inst['data-id'],
            'instance-name':inst.find('strong').text.strip()
        })
    return data




def get_status_code_response(response):
    status_code = response.status_code
    if response.status_code == 200:
        if ('недопустимый запрос' in response.text) or ('Squid Error' in response.text) or ('Access Denied') in response.text:
            success = False
            response_error = 'недопустимый запрос'
            status_code = 202
        elif ('Картотека арбитражных дел' in response.text) or ('ИНН:' in response.text):
            success = True
            response_error = 'oK' 
        else:
            try:
                response.json()
                success = True
                response_error = 'json ok'
            except:
                status_code = 888
                response_error = 'captcha'
                success = None 
    else:
        success = False
        response_error = 'неизвестно'
        status_code = 999
        if 'Доступ к сервису ограничен' in response.text:
            response_error = 'Доступ к сервису ограничен!'
    return status_code, success, response_error
   

def listor_f(data, myproxy = None):
    listorg_go = config.get('Settings', 'listorg')
    if listorg_go != '1': 
        return data
    ua = UserAgent()
    headers_list_org = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Pragma": "no-cache",
            "User-Agent":  ua.random,
            "upgrade-insecure-requests": "1",
            "sec-fetch-user": "?1",
            "sec-fetch-site": "none",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "sec-fetch-mode": "navigate",
        }
    inn = str(data['otvetchik-inn'])
    print(f'\rlistorg {inn}', end='', flush=True)
    main_page = requests.get("https://www.list-org.com/search?type=inn&val={}".format(inn),timeout=10, headers = headers_list_org ,proxies=myproxy)
    content1 = main_page.content.decode("utf-8")
    soup = BeautifulSoup(content1, "html.parser")
    table_data = soup.find("div", {"class": "org_list"})
    if not table_data: 
        return data
    else:
        orgs = table_data.findAll("p")
        if len(orgs)<=0: 
            print(inn, 'нет результата', "https://www.list-org.com/search?type=ogrn&val={}".format(inn))
            return data

    link_first = orgs[0].find("a")["href"]
    data_page = requests.get("https://www.list-org.com{}".format(link_first),headers=headers_list_org,proxies=myproxy)
    content2 = data_page.content.decode("utf-8")
    if 'хотим убедиться, что вы не робот' in content2:
        capcha = True
        print('[капча]Ошибка получения странице' )
        return data

    soup_data_page = BeautifulSoup(content2, "html.parser")
    ps = soup_data_page.findAll('p')
    json_data = {}
    for p in ps:
        if p.find('i'):
            key = p.find('i').text
            json_data[key.replace(':','')] = p.text.replace(key,'')

    founders =  soup_data_page.find('div',{'id':'founders'})
    json_data['founder'] = {
        'inn':founders.findAll('tr')[1].findAll('td')[1].text,
        'name':founders.findAll('tr')[1].findAll('td')[0].text
        }
    data['listorg'] = json_data
    return data
        


def rusprofile(data):
    inn = str(data['otvetchik-inn'])
    print(f'\rusprofile {inn}', end='', flush=True)
    response = requests.get('https://www.rusprofile.ru/ajax.php?&query={}&action=search'.format(inn))
    data = response.json()['ul'][0]
    print(data)
    result = {}
    # json_data['founder'] = {
    #     'inn':data,
    #     'name':data
    #     }
    result['rusprofile'] = data
    return result




def da_data(data):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Token {}".format(token_dadata()) 
    }
    dadata = requests.post('https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party',data=json.dumps({ "query": str(data['otvetchik-inn']) }), headers = headers).json()
    if 'suggestions' in dadata: 
        if len(dadata['suggestions'])!=0:
            data['dadata-otvetchik'] = dadata['suggestions'][0]
    return data


def cach_inn(name = "result.xls"):
    path = './data/cach.json'
    import xlrd
    try:
        with open(path) as f: data = json.loads(f.read())
    except:  data = {}
    file_loc = (name)
    py_xl = xlrd.open_workbook(file_loc)
    for py_sheet in py_xl.sheets():
        for row in range(2,py_sheet.nrows):
            name = py_sheet.cell_value (row, 0)
            inn = py_sheet.cell_value (row, 2)
            try: uid = py_sheet.cell_value (row, 9)
            except: uid = ''
            if len(uid)<5: continue
            if uid in data: continue
            if len(inn)<5: continue

            data[uid] = inn
            # проверить записан в базе или нет

        
    with open(path, 'w', encoding="utf-8") as f: f.write(json.dumps(data))

def get_inn_cach(uid):
    path = './data/cach.json'
    with open(path) as f: data = json.loads(f.read())
    if uid in data: return data[uid]
    return ''

def dadata_card_parser(data,myproxy = {'http': 'http://Yp5nub:HYjVYpuVuP4e@mproxy.site:10293', 'https': 'https://Yp5nub:HYjVYpuVuP4e@mproxy.site:10293'}):
    
    myproxy = None
    dadatacard_go = config.get('Settings', 'dadatacard')
    if dadatacard_go != '1':   return data 
    inn = data.get('otvetchik-inn', None)

    
    if inn is None: 
        print('нет инн')
        return data
    
    if len('550514260066') == len(inn):
        data['dadata-card'] = {
            'inn':f'{inn}',
            'name':data.get('otvetchik')
            }
        return data

    print(f'dadata card {inn}')

    link = f'https://dadata.ru/find/party/{inn}/'
    ua = UserAgent()
    headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Pragma": "no-cache",
            "User-Agent":  ua.random,
            "upgrade-insecure-requests": "1",
            "sec-fetch-user": "?1",
            "sec-fetch-site": "none",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "sec-fetch-mode": "navigate",
        }

    data_page = requests.get(link,timeout=15, headers = headers ,proxies=myproxy)
    content2 = data_page.content.decode("utf-8")
    print(content2)
    # Парсинг HTML-контента с использованием BeautifulSoup
    soup = BeautifulSoup(content2, 'html.parser')
    # Извлечение информации о генеральном директоре и его ИНН
    name = soup.find('h1', {'data-test': 'name'})
    director_info = soup.find('span', {'data-test': 'manager-name'})
    inn_info = soup.find('span', {'data-test': 'manager-inn'})
    print(name,director_info,inn_info)
    # Извлечение текста из элементов

    if director_info:
        director_name = director_info.get_text(strip=True)
    else: return data
    director_inn = inn_info.get_text(strip=True) if inn_info else 'Не найдено'

    # Вывод результата
    print(f'Генеральный директор: {director_name}')
    print(f' {director_inn}')

    data['dadata-card'] = {
        'inn':director_inn,
        'name':director_name
        }
    return data



def glaz_boga_phones(data,myproxy = None):
    # izal code 
    # import functions inside this functions 
    # get bot name from config 
    # test pull request

    glazboga_go = config.get('Settings', 'glazboga')
    if glazboga_go != '1':   return data 
    if 'dadata-card' not in data: return data 

    # ------- input -----------
    bot_name = config.get('Telegram', 'glazbot')
    search_input_for_bot = f"{data['dadata-card']['name']} {data['dadata-card']['inn']}"
    # ИП АТКНИН ИВАН ИВАНОВИЧ 550514260066
    # ------- / input -----------
    

    data['glazboga'] = {
        'phones':''
    }
    return data

if __name__ == '__main__':
    dadata_card_parser({'otvetchik-inn':'7708298348'})