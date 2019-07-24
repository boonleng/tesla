#!/usr/local/bin/python3

"""
    getStat.py
    Tesla

    @author: Boonleng Cheong

    Updates

    0.1    - 7/21/2019
           - Started

"""

import sys

MIN_PYTHON = (3, 4)
if sys.version_info < MIN_PYTHON:
    sys.exit('Python %s or later is required.\n' % '.'.join("%s" % n for n in MIN_PYTHON))

import os
import re
import time
import argparse
import logging
import requests
import json

__version__ = '1.0.2'

logger = logging.getLogger('Tesla')
folders = ['~/logs', '~/Documents/Tesla/logs']
logfile = None
for folder in folders:
    folder = os.path.expanduser(folder)
    if os.path.exists(folder):
        logfile = '{}/tesla-{}.log'.format(folder, time.strftime('%Y%m%d', time.localtime(time.time())))
if logfile is None:
    logfile = 'messages.log'
# print(logfile)
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
logging.Formatter.converter = time.gmtime

os.sys.path.append(os.path.expanduser('~/.ssh'))

import tesla

url = 'https://owner-api.teslamotors.com/api/1/vehicles/{}/vehicle_data'.format(tesla.vehicle_id)
headers = {
    'Authorization': 'Bearer {}'.format(tesla.token)
}

g = requests.get(url, headers=headers)

data = g.json()['response']

if data is None:
    print('Vehicle is sleeping')
else:
    jsonString = json.dumps(data)
    # print(jsonString)
    now = time.localtime(time.time())
    path = '{}/{}'.format(os.path.expanduser('~/Documents/Tesla/'), time.strftime('%Y%m%d', now))
    if not os.path.exists(path):
        os.mkdir(path)
    filename = '{}/{}'.format(path, time.strftime('%Y%m%d-%H%M.json', now))
    with open(filename, 'w') as fid:
        fid.write(jsonString)
        fid.close()
