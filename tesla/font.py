# Font

import os
import sys
import zipfile
import matplotlib
import matplotlib.font_manager
import urllib.request

from . import base

folder = 'fonts'

class Properties:
    def __init__(self, scale=1.0, force_refresh=False):
        # Check if .../fonts/HelveticaNeueBold.ttf exists
        if not os.path.exists(folder):
            os.makedirs(folder)
        file = '{}/HelveticaNeueLight.ttf'.format(folder)
        if not os.path.isfile(file) or force_refresh:
            base.logger.info('My favorite fonts are not found. Downloading from my father\'s server...')
            urllib.request.urlretrieve('https://arrc.ou.edu/iradar/fonts.zip', 'fonts.zip')
            with zipfile.ZipFile('fonts.zip') as zipped:
                for info in zipped.infolist():
                    file = '{}/{}'.format(folder, info.filename)
                    base.logger.debug('Unzipping file {} ...'.format(info.filename))
                    base.logger.debug('-> {} ...'.format(file))
                    with open(file, 'wb') as outfile:
                        with zipped.open(info) as zippedfile:
                            outfile.write(zippedfile.read())
            if os.path.isfile(file):
                base.logger.info('Fonts downloaded.')
            os.remove('fonts.zip')

        file = '{}/HelveticaNeueBold.ttf'.format(folder)

        self.tick = matplotlib.font_manager.FontProperties(fname=file, size=12.0*scale)
        self.title = matplotlib.font_manager.FontProperties(fname=file, size=16.0*scale)
        self.symbol = matplotlib.font_manager.FontProperties(fname=file, size=36.0*scale)

        self.label_big = matplotlib.font_manager.FontProperties(fname=file, size=16.0*scale)
        self.label_small = matplotlib.font_manager.FontProperties(fname=file, size=12.0*scale)
        self.label_medium = matplotlib.font_manager.FontProperties(fname=file, size=14.0*scale)
