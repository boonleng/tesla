#!/usr/local/bin/python3

__version__ = '0.9'

import tesla
import argparse

#
#   M  A  I  N
#

if __name__ == '__main__':
    # First things first, parse all the arguments
    usage = '''
    getUserToken.py [options]

    examples:

        getUserToken.py -u USERNAME -p PASSWORD
    '''
    parser = argparse.ArgumentParser(prog='getUserToken', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-u', '--username', help='specify username')
    parser.add_argument('-p', '--password', help='specify password')
    parser.add_argument('-v', default=0, action='count', help='increase the verbosity level')

    args = parser.parse_args()

    if args.v > 1:
        tesla.showDebugMessages()
    elif args.v:
        tesla.showInfoMessages()

    # Log an entry
    tesla.logger.debug('--- Started ----------')

    tesla.logger.debug('args.u = {}   args.p = {}'.format(args.username, args.password))
