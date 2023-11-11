import sys
import re
from xlwt import Workbook, easyxf
from os import walk
import json

def doxl(data, ws):
    '''Read raw account number and name strings, separate the data and
       write to an excel spreadsheet.  Properly capitalize the account
       names and mark cells with no account number as 99999 with red fill
       '''
   
    
    ws.write(0, 0, 'Дата иска')
    ws.write(0, 1, 'ИНН Ответчика')
    ws.write(0, 2, 'С кем спор (Истец)')
    ws.write(0, 3, 'ИНН ГЕНДИРА Ответчика')
    ws.write(0, 4, 'ФИО Гендира Ответчика')
    ws.write(0, 5, 'Номера телефонов ЛПР')
    ws.write(0, 6, 'Цена иска')
    ws.write(0, 7, 'Номер дела')
    
    r = 1
    for line in data:
        ws.write(r, 0, line.get('1'))
        ws.write(r, 1, line.get('otvetchik-inn'))
        ws.write(r, 2, line.get('istec'))
        ws.write(r, 3, line.get('1'))
        ws.write(r, 4, line.get('1'))
        ws.write(r, 5, line.get('1'))
        ws.write(r, 6, line.get('1'))
        ws.write(r, 7, 'https://kad.arbitr.ru/'+line.get('uid'))
        r += 1


def to_excel(list_inn):
    wb = Workbook()
    for inn in list_inn:
        ws = wb.add_sheet(inn)
        path = f"data/{inn}/"
        f = []
        for (dirpath, dirnames, filenames) in walk(path):
            # data 
            # # Opening JSON file
            with open(path+f'{filenames}'):
                data = json.load(f)
                doxl(data, ws)

    wb.save(f'result.xls')