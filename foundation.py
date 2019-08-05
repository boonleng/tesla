import os
import glob
import time
import json
import logging
import requests
import datetime

# Import the token from a secure location
os.sys.path.append(os.path.expanduser('~/.ssh'))
import tesla

# Some global constants
logger = logging.getLogger('Tesla')
dataLogHome = os.path.expanduser('~/Documents/Tesla')

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

def requestData():
    url = 'https://owner-api.teslamotors.com/api/1/vehicles/{}/vehicle_data'.format(tesla.vehicle_id)
    headers = {
        'Authorization': 'Bearer {}'.format(tesla.token)
    }
    res = requests.get(url, headers=headers)
    dat = res.json()['response']
    return dat

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

def getDataInHTML(figsize=(900, 640), padding=0.04):

    tt, dd = getCalendarArray()

    # Size in pixels
    w = figsize[0] / (7 + 6 * padding)
    h = figsize[1] / (4.5 + 3 * padding)

    # Padding in pixels
    o = w * padding

    code = '<html>'
    code += '<head>'
    code += '<meta charset="UTF-8">'
    code += '<style type="text/css">'
    code += '@font-face {font-family:"Helvetica Neue"; src:url(fonts/HelveticaNeueLight.ttf)} '
    code += 'html {font-family: "Helvetica Neue", Arial, sans-serif; font-size:10pt} '
    code += '.box-container {{display:block; position:relative; top:10px; margin:0 auto; width:{}px; height:{}px; background-color:white}} '.format(figsize[0], figsize[1])

    code += '.box {{display:block; position:absolute; width:{}px; height:{}px; border:solid 1px #aaa}}'.format(w, h)
    code += '.title {display:block; position:absolute; top:0} '
    code += '.titleMonth, .titleYear {display:inline-block; font-size:2.0em;} '
    code += '.titleMonth {font-weight:500} '
    code += '.titleYear {margin-left:0.25em} '
    code += '.dayOfWeek {{display:block; position:absolute; width:{}px; height:{}px; text-align:right}} '.format(w, 0.2 * h)

    code += '.dayLabel, .titleDayLabel {display:block; position:absolute; top:5px; right:5px; font-size:1.1em; z-index:100} '
    code += '.titleDayLabel {font-size:1.2em} '
    code += '.otherMonth {color:#aaa;} '
    code += '.batteryLevel {{display:block; position:absolute; bottom:0; width:{}%; background-color:#99ff00; z-index:0}} '.format(100)
    code += '.lowCharge {background-color:#ffcc00} '

    code += '.info {{display:block; position:absolute; bottom:10%; width:{}%; margin:0 {}%; padding:0; text-align:center}} '.format(100.0 * (1.0 - padding), 50.0 * padding)
    code += '.textInfo {display:block; width:100%} '
    code += '.large {font-size:1.8em; font-weight:500; font-stretch:extra-expanded; margin-bottom:0.3em} '
    code += '.medium {line-height:1.2em} '
    code += '.tiny {line-height:0.8em} '

    code += '.iconBar {display:block; position:absolute; top:8px; left:8px; width:100%} '
    code += 'img.icon {float:left; margin:0; width:18px; padding:2px} '
    code += '</style>'
    code += '</head>'

    code += '<body>'

    code += '<div class="box-container">'

    code += '<div class="title">'
    code += '<span class="titleMonth">{}</span><span class="titleYear">{}</span>'.format(tt[-1][0].strftime('%B'), tt[0][0].strftime('%Y'))
    code += ' <span class="titleMonth"></span>'
    code += '</div>'

    # Use the latest day to decide the target month
    targetMonth = tt[-1][0].month

    # The top row show days of the week
    for i in range(7):
        x = i * (w + o)
        y = 0.28 * h
        code += '<div class="dayOfWeek" style="left:{:.2f}px; top:{:.2f}px">'.format(x, y,)
        code += '<span class="titleDayLabel">{}</span>'.format(tt[0][i].strftime('%a'))
        code += '</div>'

    # Odometer reading from the previous day
    o1 = 0.0

    # Now we go through the days
    mo = tt[0][0].month
    for j in range(len(tt)):
        for i in range(len(tt[j])):
            x = i * (w + o)
            y = j * (h + o) + 0.5 * h
            xc = x + 0.5 * w

            # Background
            code += '<div class="box" style="left:{:.2f}px; top:{:.2f}px">'.format(x, y)

            # The day label.
            if mo != tt[j][i].month:
                mo = tt[j][i].month
                dayString = '{}'.format(tt[j][i].strftime('%b %-d'))
            else:
                dayString = '{}'.format(tt[j][i].strftime('%-d'))
            if targetMonth != mo:
                elementClass = ' otherMonth'
            else:
                elementClass = ''
            code += '<span class="dayLabel{}">{}</span>'.format(elementClass, dayString)

            # Skip the day if there is no data
            if dd[j][i] is None:
                code += '</div>'
                continue

            # Battery level
            dayArray = dd[j][i]
            batteryLevel = dayArray[-1]['charge_state']['battery_level']
            if batteryLevel <= 60.0:
                elementClass = ' lowCharge'
            else:
                elementClass = ''
            code += '<div class="batteryLevel{}" style="height:{}%"></div>'.format(elementClass, batteryLevel)

            # Calculate total miles driven
            if o1 == 0.0:
                o1 = dayArray[0]['vehicle_state']['odometer']
            o0 = dayArray[-1]['vehicle_state']['odometer']
            delta_o = o0 - o1
            o1 = o0

            #
            sw = dayArray[-1]['vehicle_state']['car_version']

            # Icon bar using the information derived earlier
            code += '<div class="iconBar">'
            if any([d['charge_state']['charging_state'] == 'Charging' for d in dayArray]):
                code += '<img class="icon" src="blob/charge-0.png">'
            if delta_o > 20:
                code += '<img class="icon" src="blob/wheel.png">'
            code += '</div>'

            # Lines of information
            code += '<div class="info">'
            code += '<span class="textInfo large">{}%</span>'.format(batteryLevel)
            code += '<span class="textInfo medium">{}</span>'.format(tt[j][i].strftime('%I:%M %p'))
            code += '<span class="textInfo medium">{:.1f} mi ({})</span>'.format(delta_o, len(dayArray))
            code += '<span class="textInfo small">{}</span>'.format(sw)
            code += '</div>'

            code += '</div>'

    code += '</div>'
    code += '</body>'
    code += '</html>'

    return code
