import sys
import re
from xlwt import Workbook, easyxf,Formula,Font, XFStyle
from os import walk
import json
from datetime import datetime

def write_head(ws):
    print('добавляем загаловки для странице')
    heads = [
        'Ответчик', 
        'Дата иска',
        'ИНН Ответчика',
        'С кем спор (Истец)',
        'ИНН ГЕНДИРА Ответчика',
        'ФИО Гендира Ответчика',
        'Номера телефонов ЛПР',
        'Цена иска',
        'Номер дела',
        'uid',
    ]
    f = Font()
    # f.height = 20*72
    f.bold = True
    # f.colour_index = 4

    h_style = XFStyle()
    h_style.font = f

    for i in range(9):
        ws.write(0, i, heads[i],h_style)

    size = [
        40,15,15,20,
        15,20,10,10,
        20,20,20,20
        ]
    for i in range(9):
        col = ws.col(i)
        col.width = 256 * size[i]   

    return ws

def doxl(data, ws,r = 1):
    uid = data.get('uid')
    case = data.get('case')
    n = "HYPERLINK"
    try:
        otvetchic_gendir = data.get('dadata-otvetchik',{}).get('data',{}).get('management',{}).get('name','-') 
    except:
        otvetchic_gendir = '-'
        # print(data.get('dadata-otvetchik',{}))
    try:
        dadatacard_inn_gen = data.get('dadata-card',{}).get('inn','-')
        dadatacard_name_gen = data.get('dadata-card',{}).get('name','-')
    except:
        dadatacard_inn_gen = '-'
        dadatacard_name_gen = '-'

    ws.write(r, 0, data.get('otvetchik'))
    ws.write(r, 1, data.get('hearingDate'))
    ws.write(r, 2, data.get('otvetchik-inn'))
    ws.write(r, 3, data.get('istec'))
    ws.write(r, 4, dadatacard_inn_gen)
    ws.write(r, 5, dadatacard_name_gen)
    ws.write(r, 6, data.get('listorg',{}).get('Телефон','-'))
    ws.write(r, 7, data.get('1'))
    ws.write(r, 8,  Formula(n + f'("https://kad.arbitr.ru/Card/{uid}";"{case}")'))
    ws.write(r, 9, uid)
    return ws

def to_excel(list_inn):
    from functions import get_inn_cach
    print('переписываем EXCEL')
    wb = Workbook()
    ws = {}
    for inn in list_inn:

        ws[inn] = wb.add_sheet(inn)
        ws[inn] = write_head(ws[inn])
        path = f"data/{inn}/"
        f = []
        count = 0
        fnames = {}

        

        for (dirpath, dirnames, filenames) in walk(path):
            for fname in filenames:
                with open(path+f'{fname}') as f:
                    data = json.loads(f.read())
                    datetime_object = datetime.strptime(data.get('hearingDate') if data.get('hearingDate') else '01.01.1700 00:00:00', '%d.%m.%Y %H:%M:%S')
                    fnames[fname] = datetime_object
        

        fnames_sorted = sorted(fnames.items(), key=lambda x:x[1])

        count+=1
        for fname_l in fnames_sorted:
            fname = fname_l[0]
            with open(path+f'{fname}') as f:
                count+=1
                data = json.loads(f.read())
                
                # с кэша забираем инн
                case_id = data.get('otvetchik-inn','') if data.get('otvetchik-inn') else ''
                if len(case_id)<5:
                    print('получаем инн отвечика c кэша')
                    otvetchik_inn = get_inn_cach(data.get('uid'))
                    if len(otvetchik_inn)>5: 
                        data['otvetchik-inn'] = otvetchik_inn
                        with open(path+f'{fname}', 'w', encoding="utf-8") as f: f.write(json.dumps(data))

                ws[inn] = doxl(data, ws[inn], r = count)
    try:
        wb.save(f'result.xls')
        print('все готово)')
    except:
        print('ОШИБКА, не смогли сохранить EXCEL, не забывайте закрывать перед перезаписью')
