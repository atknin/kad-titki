# !/usr/bin/env python3
import requests
import time
import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

while True:
    starts = requests.get('http://app.legaltrack.ru/api/v4/company/get-for-update').json()
    print(starts)
    if len(starts['data']) == 0:
        print('sleep 127')
        time.sleep(200)
        continue


    for data in starts['data']:
        inn = data['inn']
        print(inn)
        is_synced = '1' if data['is_synced'] else '0'
        print(sys.executable, BASE_DIR + "/search_inn.py", inn, is_synced)
        cmd = [sys.executable, BASE_DIR + "/search_inn.py", inn, is_synced]

        timeout = 30
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            out, err = process.communicate(timeout=timeout)


        except subprocess.TimeoutExpired:
            arr = {'inn': inn, 'cases': [],'error': True}
            url_update = 'http://app.legaltrack.ru/api/v4/company/update-inn'
            resp = requests.post(url_update, json=arr)
            print(f'Timeout for ({timeout}s) expired')
            process.kill()
