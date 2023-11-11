import sys
import re
from xlwt import Workbook, easyxf,Formula
from os import walk
import json

def write_head(ws):
    heads = [
        'Ответчик', 
        'ИНН Ответчика',
        'Дата иска'
        'ИНН Ответчика',
        'С кем спор (Истец)',
        'ИНН ГЕНДИРА Ответчика',
        'ФИО Гендира Ответчика',
        'Номера телефонов ЛПР',
        'Цена иска',
        'Номер дела'
    ]
    for i in range(9):

        ws.write(0, i, heads[i])

    for i in range(7):
        col = ws.col(i)
        col.width = 256 * 20   

    return ws

def doxl(data, ws,r = 1):
    uid = data.get('uid')
    case = data.get('case')
    n = "HYPERLINK"
    ws.write(r, 0, data.get('otvetchik'))
    ws.write(r, 1, data.get('1'))
    ws.write(r, 2, data.get('otvetchik-inn'))
    ws.write(r, 3, data.get('istec'))
    ws.write(r, 4, data.get('1'))
    ws.write(r, 5, data.get('1'))
    ws.write(r, 6, data.get('1'))
    ws.write(r, 7, data.get('1'))
    ws.write(r, 8,  Formula(n + f'("https://kad.arbitr.ru/{uid}";"{case}")'))
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