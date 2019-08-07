import os
import time
import logging

# Some global constants
site = 'owner-api.teslamotors.com'
rcFile = os.path.expanduser('~/.teslarc')
dataLogHome = os.path.expanduser('~/Documents/Tesla')
logger = logging.getLogger('Tesla')

# Loggin levels
def showMessageLevel(level=logging.WARNING):
    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(handler)
    else:
        handler = logger.landlers[0]
        handler.setLevel(level)

def showWarningMessages():
    showMessageLevel(logging.WARNING)

def showDebugMessages():
    showMessageLevel(logging.DEBUG)

def showInfoMessages():
    showMessageLevel(logging.INFO)

# Data log folder
folders = ['~/logs', '{}/logs'.format(dataLogHome)]
logfile = None
for folder in folders:
    folder = os.path.expanduser(folder)
    if os.path.exists(folder):
        logfile = '{}/tesla-{}.log'.format(folder, time.strftime('%Y%m%d', time.localtime(time.time())))
if logfile is None:
    logfile = 'messages.log'
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%H:%M:%S')
logging.Formatter.converter = time.gmtime

logger.setLevel(logging.INFO)
