#!/usr/local/bin/python3

"""
    getStat.py
    Tesla Data Logger

    @author: Boonleng Cheong

    Updates

    1.2    - 8/6/2019
           - Moved a lot of reusable functions to data.py

    1.1    - 8/5/2019
           - Moved a lot of reusable functions to base.py

    1.0    - 8/2/2019
           - It is working. We can schedule this to run routinely through a cronjob

    0.1    - 7/21/2019
           - Started

"""

__version__ = '1.2'

import os
import time
import json
import argparse

import base
import data


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

    # Set the logger to output something if verbosity flag is set
    if args.v > 1:
        base.showDebugMessages()
    elif args.v:
        base.showInfoMessages()

    # Log an entry
    base.logger.debug('--- Started ----------')
    base.logger.info('Tesla Data Logger {}'.format(__version__))

    dat = data.requestData()

    if dat is None:
        base.logger.info('Vehicle is sleeping')
    else:
        jsonString = json.dumps(dat)

        base.logger.info('Data received. battery_level = {}   range = {} / {}   write = {}'.format(
            dat['charge_state']['battery_level'],
            dat['charge_state']['battery_range'],
            dat['charge_state']['ideal_battery_range'],
            args.write))
        if args.write:
            now = time.localtime(time.time())
            path = '{}/{}'.format(base.dataLogHome, time.strftime('%Y%m%d', now))
            if not os.path.exists(path):
                os.mkdir(path)
            filename = '{}/{}'.format(path, time.strftime('%Y%m%d-%H%M.json', now))
            with open(filename, 'w') as fid:
                fid.write(jsonString)
                fid.close()
            code = data.getDataInHTML()
            with open(os.path.expanduser('~/Developer/tesla/calendar.html'), 'w') as fid:
                fid.write(code)
                fid.close()
