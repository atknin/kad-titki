import sys
import re
from xlwt import Workbook, easyxf,Formula,Font, XFStyle
from os import walk
import json

def write_head(ws):
    heads = [
        'Ответчик', 
        'Дата иска',
        'ИНН Ответчика',
        'С кем спор (Истец)',
        'ИНН ГЕНДИРА Ответчика',
        'ФИО Гендира Ответчика',
        'Номера телефонов ЛПР',
        'Цена иска',
        'Номер дела'
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
    ws.write(r, 0, data.get('otvetchik'))
    ws.write(r, 1, data.get('hearingDate'))
    ws.write(r, 2, data.get('otvetchik-inn'))
    ws.write(r, 3, data.get('istec'))
    ws.write(r, 4, data.get('1'))
    ws.write(r, 5, data.get('1'))
    ws.write(r, 6, data.get('1'))
    ws.write(r, 7, data.get('1'))
    ws.write(r, 8,  Formula(n + f'("https://kad.arbitr.ru/Card/{uid}";"{case}")'))
    return ws

def to_excel(list_inn):
    wb = Workbook()
    ws = {}
    for inn in list_inn:

        ws[inn] = wb.add_sheet(inn)
        ws[inn] = write_head(ws[inn])
        path = f"data/{inn}/"
        f = []
        count = 0
        for (dirpath, dirnames, filenames) in walk(path):
            for fname in filenames:
                count+=1
                with open(path+f'{fname}') as f:
                    data = json.loads(f.read())
                    ws[inn] = doxl(data, ws[inn], r = count)
                    
    wb.save(f'result.xls')