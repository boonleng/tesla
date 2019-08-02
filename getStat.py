#!/usr/local/bin/python3

"""
    getStat.py
    Tesla Data Logger

    @author: Boonleng Cheong

    Updates

    1.0    - 8/2/2019
           - It is working. We can schedule this to run routinely through a cronjob

    0.1    - 7/21/2019
           - Started

"""

__version__ = '1.0'

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

logger = logging.getLogger('Tesla')
folders = ['~/logs', '~/Documents/Tesla/logs']
logfile = None
for folder in folders:
    folder = os.path.expanduser(folder)
    if os.path.exists(folder):
        logfile = '{}/tesla-{}.log'.format(folder, time.strftime('%Y%m%d', time.localtime(time.time())))
if logfile is None:
    logfile = 'messages.log'
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
logging.Formatter.converter = time.gmtime

os.sys.path.append(os.path.expanduser('~/.ssh'))

import tesla

def requestData():
    url = 'https://owner-api.teslamotors.com/api/1/vehicles/{}/vehicle_data'.format(tesla.vehicle_id)
    headers = {
        'Authorization': 'Bearer {}'.format(tesla.token)
    }
    res = requests.get(url, headers=headers)
    dat = res.json()['response']
    return dat

#
#     M  A  I  N
#

if __name__ == '__main__':
    # First things first, parse all the arguments
    usage = '''
        getStat.py [options]

        examples:

        getStat.py
        getStat.py -v
        '''
    parser = argparse.ArgumentParser(prog='getStat', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-w', '--write', default=False, action="store_true", help='writes the results to a file')
    parser.add_argument('-v', default=0, action='count', help='increase the verbosity level')
    args = parser.parse_args()

    # Another stream handler to show output on screen
    handler = logging.StreamHandler()
    if args.v > 1:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif args.v:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
    logger.addHandler(handler)

    # Log an entry
    logger.debug('--- Started ----------')
    logger.info('Tesla Data Logger {}'.format(__version__))

    dat = requestData()

    if dat is None:
        if args.v:
            logger.info('Vehicle is sleeping')
    else:
        jsonString = json.dumps(dat)

        logger.info('Data received. battery_level = {}   range = {} / {}   write = {}'.format(
            dat['charge_state']['battery_level'],
            dat['charge_state']['battery_range'],
            dat['charge_state']['ideal_battery_range'],
            args.write))
        if args.write:
            now = time.localtime(time.time())
            path = '{}/{}'.format(os.path.expanduser('~/Documents/Tesla/'), time.strftime('%Y%m%d', now))
            if not os.path.exists(path):
                os.mkdir(path)
            filename = '{}/{}'.format(path, time.strftime('%Y%m%d-%H%M.json', now))
            with open(filename, 'w') as fid:
                fid.write(jsonString)
                fid.close()

