#!/usr/local/bin/python

__version__ = '1.0'

import os
import tesla

code = tesla.getDataInHTML()
with open(os.path.expanduser('~/Developer/tesla/calendar.html'), 'w') as fid:
    fid.write(code)
    fid.close()
tesla.logger.info('HTML calendar updated.')
