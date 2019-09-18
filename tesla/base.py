import os
import time
import logging

# Some global constants
site = 'owner-api.teslamotors.com'
rcFile = os.path.expanduser('~/.teslarc')
logHome = os.path.expanduser('~/logs')
dataLogHome = os.path.expanduser('~/Documents/Tesla')
logger = logging.getLogger('Tesla')

def setLogPrefix(prefix):
    logfile = '{}/{}-{}.log'.format(logHome, prefix, time.strftime('%Y%m%d', time.localtime(time.time())))
    fileHandler = logging.FileHandler(logfile, 'a')
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
    logger.addHandler(fileHandler)
    return logfile


def getLogfile():
    for h in logger.handlers:
        if isinstance(h, logging.FileHandler):
            return h.baseFilename


def showMessageLevel(level):
    if len(logger.handlers) == 1:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%H:%M:%S'))
        logger.addHandler(handler)
    for h in logger.handlers:
        if not isinstance(h, logging.FileHandler):
            h.setLevel(level)
    if level < logging.INFO:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)


def showWarningMessages():
    showMessageLevel(logging.WARNING)


def showDebugMessages():
    showMessageLevel(logging.DEBUG)


def showInfoMessages():
    showMessageLevel(logging.INFO)

# ----------------------------

# Logger
if os.path.exists(logHome):
    setLogPrefix('tesla')
showWarningMessages()
