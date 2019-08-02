import os
import logging

logger = logging.getLogger('Tesla')

def showMessageLevel(level):
    logger.setLevel(level)
    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
        logger.addHandler(handler)

def showDebugMessages():
    showMessageLevel(logging.DEBUG)

def showInfoMessages():
    showMessageLevel(logging.INFO)

def shortenPath(path, n):
    parts = path.split('/')
    return '...{}'.format('/'.join(parts[-n:])) if len(parts) > n else path
