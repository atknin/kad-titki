import os
import requests 
import json 
from bs4 import BeautifulSoup, element
from datetime import datetime
import itertools
myproxy = {'http':'http://ueLsat:BUdqGP@87.247.146.95:8000'}
stat_base_url = 'http://app.legaltrack.ru'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(BASE_DIR, 'data')
if not os.path.isdir(data_path):
    os.mkdir(data_path)

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
    global myproxy
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
        
        element['hearingDate'] = line.find("div",{'class':'civil'})['title'] if line.find("div",{'class':'civil'})  else None
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
        element['otvetchik-inn'] = div_inn.text.replace('\t','').replace('\r','').replace('  ','').replace('\n','').strip().split(':')[1] if div_inn else None
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
   


def da_data(data):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Token 731d578f91142b6ff8e3b5659badb868b78dafae"
    }
    dadata = requests.post('https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party',data=json.dumps({ "query": str(data['otvetchik-inn']) }), headers = headers).json()
    if 'suggestions' in dadata: 
        if len(dadata['suggestions'])!=0:
            data['dadata-otvetchik'] = dadata['suggestions'][0]
    return data
