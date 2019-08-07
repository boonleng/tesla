#!/usr/local/bin/python

__version__ = '1.0'

import os
import data

code = data.getDataInHTML()
with open(os.path.expanduser('~/Developer/tesla/calendar.html'), 'w') as fid:
    fid.write(code)
    fid.close()
