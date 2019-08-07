import os
import json
import glob
import time
import logging
import requests
import datetime

import account

# Some global constants
site = 'owner-api.teslamotors.com'
rcFile = os.path.expanduser('~/.teslarc')
dataLogHome = os.path.expanduser('~/Documents/Tesla')
logger = logging.getLogger('Tesla')
config = account.getConfig()

# Loggin levels
def showMessageLevel(level=logging.WARNING):
    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S'))
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
logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
logging.Formatter.converter = time.gmtime

logger.setLevel(logging.INFO)

def shortenPath(path, n):
    parts = path.split('/')
    return '...{}'.format('/'.join(parts[-n:])) if len(parts) > n else path

def requestData(index=0):
    vehicleId = config['cars'][index]['id']
    url = 'https://owner-api.teslamotors.com/api/1/vehicles/{}/vehicle_data'.format(vehicleId)
    headers = {
        'Authorization': 'Bearer {}'.format(config['token']['access_token'])
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()['response']
    return None

def objFromFile(filename):
    with open(filename, 'r') as fobj:
        json_str = fobj.readline()
        fobj.close()
    return json.loads(json_str)

def getLatestDays(count=31):
    folders = glob.glob('{}/2*'.format(dataLogHome))
    folders.sort()

    t = []
    d = []
    for folder in folders[-count:]:
        files = glob.glob('{}/*.json'.format(folder))
        files.sort()
        dd = []
        for file in files:
            #print('{}'.format(file))
            data = objFromFile(file)
            dd.append(data)
        d.append(dd)
        o = d[-1][-1]['charge_state']
        t.append(datetime.datetime.fromtimestamp(o['timestamp'] / 1000))
        # print('{} -> {}% {} {}'.format(os.path.basename(file), o['battery_level'], o['charging_state'], t[-1].weekday()))
    return t, d

def getCalendarArray():
    # Get the data from the latest 31 days
    t, d = getLatestDays()

    # Find the 4th Sunday before present day
    t0 = t[-1]
    oneday = datetime.timedelta(days=1)
    while t0.weekday() != 6:
        t0 -= oneday
    t0 -= datetime.timedelta(days=21)
    # display('{}'.format(t0.strftime('%Y/%m/%d %H:%M %A')))

    # The first Sunday
    t0 = datetime.datetime.strptime(t0.strftime('%Y-%m-%d'), '%Y-%m-%d')
    # display('{}'.format(t0.strftime('%Y/%m/%d %H:%M %A')))

    # Group the weeks
    tt = []
    dd = []
    k = 0

    # Make a 4-week array of data arrays
    for i in range(4):
        tw = []
        dw = []
        for i in range(7):
            if k < len(t) and t0 <= t[k] and t[k] < (t0 + oneday):
                tw.append(t[k])
                dw.append(d[k])
                k += 1
            else:
                tw.append(t0)
                dw.append(None)
            t0 += oneday
        tt.append(tw)
        dd.append(dw)

    return tt, dd

def getDataInHTML(padding=0.05):

    tt, dd = getCalendarArray()

    # Initial figsize to get things started
    figsize = (900, 135 * len(tt) + 90)

    # Size in pixels
    w = int(figsize[0] / (7 + 6 * padding))
    h = int(figsize[1] / (4.5 + 3 * padding))

    # Padding in pixels
    o = int(padding * w)

    # Pixel-perfect figsize
    figsize = (7 * (w + o) - o + 1, len(tt) * (h + o) - o + 90 + 1)

    # Find the first datalog that is valid
    week = next(w for w in dd[::-1] if any(w))
    day = next(d for d in week[::-1] if d is not None)
    d = day[-1]

    lastUpdate = datetime.datetime.fromtimestamp(d['vehicle_state']['timestamp'] / 1000)

    code = '<html>'
    code += '<head>\n'
    code += '<meta charset="UTF-8">\n'
    code += '<style type="text/css">\n'
    code += '@font-face {font-family:"Helvetica Neue"; src:url(fonts/HelveticaNeueLight.ttf)}\n'
    code += 'html {font-family: "Helvetica Neue", Arial, sans-serif; font-size:10pt}\n'
    code += '.box-container {{display:block; position:relative; top:10px; margin:0 auto; width:{:.2f}px; height:{:.2f}px; background-color:white}}\n'.format(figsize[0], figsize[1])
    code += '\n'
    code += '.title {display:block; position:absolute; top:0}\n'
    code += '.titleMonth, .titleYear {display:inline-block; font-size:2.4em;}\n'
    code += '.titleMonth {font-weight:500}\n'
    code += '.titleYear {margin-left:0.25em}\n'
    code += '.vin {display:block; position:absolute; right:0}\n'
    code += '.update {display:block; position:absolute; top:20px; right:0}\n'
    code += '.dayOfWeek {{display:block; position:absolute; width:{}px; height:{}px; text-align:right}}\n'.format(w, 50)
    code += '\n'
    code += '.box {{display:inline-block; position:absolute; width:{:.2f}px; height:{:.2f}px; border:solid 1px #aaa}}\n\n'.format(w, h)
    code += '.dayLabel, .titleDayLabel {display:block; position:absolute; top:5px; right:5px; font-size:1.1em; z-index:100}\n'
    code += '.today {color:#39f; font-weight:500}\n'
    code += '.titleDayLabel {font-size:1.2em}\n'
    code += '.otherMonth {color:#aaa;}\n'
    code += '.chargeLevel {{display:block; position:absolute; bottom:0; width:{}%; background-color:#88ff00; z-index:0}}\n'.format(100)
    code += '.lowCharge {background-color:#ffcc00}\n'
    code += '\n'
    code += '.info {{display:block; position:absolute; bottom:8%; width:{}%; margin:0 {}%; padding:0; text-align:center}}\n'.format(100.0 * (1.0 - padding), 50.0 * padding)
    code += '.textInfo {display:block; width:100%; margin-bottom:0.3em; line-height:1.0em}\n'
    code += '.large {font-size:1.8em; font-weight:500; font-stretch:extra-expanded}\n'
    code += '.medium {font-size:1.0em}\n'
    code += '.small {font-size:0.9em}\n'
    code += '.tiny {font-size:0.8em}\n'
    code += '\n'
    code += '.iconBar {display:block; position:absolute; top:5px; left:8px; width:100%}\n'
    code += 'img.icon {float:left; margin:0; width:16px; padding:2px}\n'
    code += '</style>\n'
    code += '</head>\n'
    code += '\n'
    code += '<body>\n'
    code += '<div class="box-container">\n'
    code += '<div class="title">\n'
    code += '<span class="titleMonth">{}</span><span class="titleYear">{}</span>\n'.format(tt[-1][0].strftime('%B'), tt[0][0].strftime('%Y'))
    code += '</div>\n'
    code += '<span class="vin medium"><b>{}</b> - {} - {}</span>\n'.format(d['vehicle_state']['vehicle_name'], d['vin'], d['vehicle_state']['car_version'])
    code += '<span class="update medium">Last Updated: {}</span>\n'.format(lastUpdate.strftime('%Y-%m-%d %I:%M %p'))

    # Use the latest day to decide the target month
    targetMonth = tt[-1][0].month

    # The top row show days of the week
    for i in range(7):
        x = i * (w + o)
        y = 60
        code += '<div class="dayOfWeek" style="left:{:.2f}px; top:{:.2f}px">\n'.format(x, y)
        code += '<span class="titleDayLabel">{}</span>\n'.format(tt[0][i].strftime('%a'))
        code += '</div>\n'

    # Odometer reading from the previous day
    o1 = 0.0

    # Now we go through the days
    mo = tt[0][0].month
    todayString = datetime.datetime.today().strftime('%-d')
    for j in range(len(tt)):
        for i in range(len(tt[j])):
            x = i * (w + o)
            y = j * (h + o) + 90
            xc = x + 0.5 * w

            # A day container
            code += '<div class="box" style="left:{:.2f}px; top:{:.2f}px">\n'.format(x, y)

            # code += '<div class="box">\n'

            # The day label.
            if mo != tt[j][i].month:
                mo = tt[j][i].month
                dayString = '{}'.format(tt[j][i].strftime('%b %-d'))
            else:
                dayString = '{}'.format(tt[j][i].strftime('%-d'))
            elementClass = ''
            if targetMonth != mo:
                elementClass += ' otherMonth'
            if dayString == todayString:
                elementClass += ' today'
            
            code += '<span class="dayLabel{}">{}</span>\n'.format(elementClass, dayString)

            # Skip the day if there is no data
            if dd[j][i]:
                # Battery level
                dayArray = dd[j][i]
                chargeLevel = dayArray[-1]['charge_state']['battery_level']
                if chargeLevel <= 60.0:
                    elementClass = ' lowCharge'
                else:
                    elementClass = ''
                code += '<div class="chargeLevel{}" style="height:{}%"></div>\n'.format(elementClass, chargeLevel)

                # Calculate total miles driven
                if o1 == 0.0:
                    o1 = dayArray[0]['vehicle_state']['odometer']
                o0 = dayArray[-1]['vehicle_state']['odometer']
                delta_o = o0 - o1
                o1 = o0

                # day
                # temp = [d['climate_state']['outside_temp'] for d in dayArray]
                # temp = np.array(temp, dtype=np.float)
                # minTemp = np.nanmin(temp) * 9 / 5 + 32.0
                # maxTemp = np.nanmax(temp) * 9 / 5 + 32.0

                # Icon bar using the information derived earlier
                code += '<div class="iconBar">\n'
                if delta_o > 1.0:
                    code += '<img class="icon" src="blob/wheel.png">\n'
                if any([d['charge_state']['charging_state'] == 'Charging' for d in dayArray]):
                    code += '<img class="icon" src="blob/charge-0.png">\n'
                code += '</div>\n'

                # Lines of information
                code += '<div class="info">\n'
                code += '<span class="textInfo large">{}%</span>\n'.format(chargeLevel)
                code += '<span class="textInfo medium">{}</span>\n'.format(tt[j][i].strftime('%-I:%M %p'))
                code += '<span class="textInfo medium">{:+.1f} mi ({})</span>\n'.format(delta_o, len(dayArray))
                code += '<span class="textInfo medium">{:.1f} mi</span>\n'.format(o0)
                code += '</div>\n'

            code += '</div>\n'

    code += '</div>\n'
    code += '</body>\n'
    code += '</html>\n'

    return code
