import sys
import re
from xlwt import Workbook, easyxf
from os import walk
import json

def write_head(ws):
    ws.write(0, 0, 'Дата иска')
    ws.write(0, 1, 'ИНН Ответчика')
    ws.write(0, 2, 'С кем спор (Истец)')
    ws.write(0, 3, 'ИНН ГЕНДИРА Ответчика')
    ws.write(0, 4, 'ФИО Гендира Ответчика')
    ws.write(0, 5, 'Номера телефонов ЛПР')
    ws.write(0, 6, 'Цена иска')
    ws.write(0, 7, 'Номер дела')

    for i in range(7):
        col = ws.col(i)
        col.width = 256 * 20   

    return ws

def doxl(data, ws,r = 1):
    ws.write(r, 0, data.get('1'))
    ws.write(r, 1, data.get('otvetchik-inn'))
    ws.write(r, 2, data.get('istec'))
    ws.write(r, 3, data.get('1'))
    ws.write(r, 4, data.get('1'))
    ws.write(r, 5, data.get('1'))
    ws.write(r, 6, data.get('1'))
    ws.write(r, 7, 'https://kad.arbitr.ru/'+data.get('uid'))
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