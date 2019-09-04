import os
import glob
import json
import time
import requests

from .base import *
from . import account

config = account.getConfig()

def requestData(index=0, retry=True):
    vehicleId = config['cars'][index]['id']
    url = 'https://owner-api.teslamotors.com/api/1/vehicles/{}/vehicle_data'.format(vehicleId)
    headers = {
        'Authorization': 'Bearer {}'.format(config['token']['access_token'])
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()['response']
    elif res.status_code == 404 and retry:
        base.logger.info('Vechicle not found. Try refreshing cars... r = {}'.format(res.status_code))
        account.updateCars()
        return requestData(index=index, retry=False)
    base.logger.info('Vechicle connection error. r = {}'.format(res.status_code))
    return None

def objFromFile(filename):
    with open(filename, 'r') as fobj:
        json_str = fobj.readline()
        fobj.close()
    return json.loads(json_str)

def getLatestDays(count=28):
    folders = glob.glob('{}/2*'.format(base.dataLogHome))
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
        t.append(o['timestamp'] / 1000)
    return t, d

def getCalendarArray(count=5):
    # Get the data from the latest 31 days
    t, d = getLatestDays(count * 7)

    # Find the 4th Sunday before present day
    k = 0
    t0 = t[-1]
    while time.localtime(t0).tm_wday != 6 and k < 7:
        t0 -= 86400
        k += 1
    if k == 7:
        print('Error. Could not find a Sunday after 7 days. Huh?')
    t0 -= (count - 1) * 7 * 86400

    # The first Sunday
    t0 = time.mktime(time.strptime(time.strftime('%Y-%m-%d', time.localtime(t0)), '%Y-%m-%d'))

    # Group the weeks
    k = 0
    tt = []
    dd = []

    # Roll forward if the data starts before the first Sunday
    while k < 7 and k < len(t) and t[k] < t0:
        k += 1

    # Make a (count)-week array of data arrays
    for _ in range(count):
        tw = []
        dw = []
        for _ in range(7):
            if k < len(t) and t0 <= t[k] and t[k] < (t0 + 86400):
                tw.append(time.localtime(t[k]))
                dw.append(d[k])
                k += 1
            else:
                tw.append(time.localtime(t0))
                dw.append(None)
            t0 += 86400
        tt.append(tw)
        dd.append(dw)

    return tt, dd

def getDataInHTML(count=4, padding=0.05, showFadeIcon=True):

    tt, dd = getCalendarArray(count)

    # Do this to ensure custom fonts are available
    import tesla.font
    prop = tesla.font.Properties()

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
    if len([w for w in dd[::-1] if any(w)]):
        week = next(w for w in dd[::-1] if any(w))
        day = next(d for d in week[::-1] if d is not None)
        d = day[-1]

        lastUpdate = time.localtime(d['vehicle_state']['timestamp'] / 1000)
    else:
        lastUpdate = None

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
    code += '.charge5 {background-color:#88ff00}\n'
    code += '.charge4 {background-color:#c3ee00}\n'
    code += '.charge3 {background-color:#ffdd00}\n'
    code += '.charge2 {background-color:#ffa133}\n'
    code += '.charge1 {background-color:#ff6666}\n'
    code += '.charge0 {background-color:#ff4499}\n'
    code += '\n'
    code += '.info {{display:block; position:absolute; bottom:8%; width:{}%; margin:0 {}%; padding:0; text-align:center}}\n'.format(100.0 * (1.0 - padding), 50.0 * padding)
    code += '.textInfo {display:block; width:100%; margin-bottom:0.3em; line-height:1.0em}\n'
    code += '.large {font-size:1.8em; font-weight:500; font-stretch:extra-expanded}\n'
    code += '.medium {font-size:1.0em}\n'
    code += '.small {font-size:0.9em}\n'
    code += '.tiny {font-size:0.8em}\n'
    code += '\n'
    code += '.iconBar {display:block; position:absolute; top:5px; left:8px; width:100%}\n'
    code += 'img.icon, .blankIcon {display:block; float:left; margin:0; width:16px; height:16px; padding:2px 3px}\n'
    code += '.fade {opacity:0.15;}'
    code += '</style>\n'
    code += '</head>\n'
    code += '\n'
    code += '<body>\n'
    code += '<div class="box-container">\n'
    code += '<div class="title">\n'
    code += '<span class="titleMonth">{}</span><span class="titleYear">{}</span>\n'.format(time.strftime('%B', tt[-1][0]), time.strftime('%Y', tt[-1][0]))
    code += '</div>\n'
    if lastUpdate:
        code += '<span class="vin medium"><b>{}</b> - {} - {}</span>\n'.format(d['vehicle_state']['vehicle_name'], d['vin'], d['vehicle_state']['car_version'])
        code += '<span class="update medium">Last Updated: {}</span>\n'.format(time.strftime('%Y-%m-%d %I:%M %p', lastUpdate))
    else:
        code += '<span class="vin medium"><b>{}</b> - {} - {}</span>\n'.format('VEHICLE_NAME', '5YJ3E1EA3JF000000', '2018.36.2 ac4a215')
        code += '<span class="update medium">Last Updated: -</span>\n'
        print('Error. No valid days')

    # Use the latest day to decide the target month
    targetMonth = tt[-1][0].tm_mon

    # The top row show days of the week
    for i in range(7):
        x = i * (w + o)
        y = 60
        code += '<div class="dayOfWeek" style="left:{:.2f}px; top:{:.2f}px">\n'.format(x, y)
        code += '<span class="titleDayLabel">{}</span>\n'.format(time.strftime('%a', tt[0][i]))
        code += '</div>\n'

    # Odometer reading and software version from the previous day
    o1 = None
    s1 = None

    # Now we go through the days
    mo = tt[-1][0].tm_mon
    todayString = time.strftime('%-d', time.localtime(time.time()))
    for j in range(len(tt)):
        for i in range(len(tt[j])):
            x = i * (w + o)
            y = j * (h + o) + 90
            xc = x + 0.5 * w

            # A day container
            code += '<div class="box" style="left:{:.2f}px; top:{:.2f}px">\n'.format(x, y)

            # The day label.
            if mo != tt[j][i].tm_mon:
                mo = tt[j][i].tm_mon
                dayString = time.strftime('%b %-d', tt[j][i])
            else:
                dayString = time.strftime('%-d', tt[j][i])
            elementClass = ''
            if targetMonth != mo:
                elementClass += ' otherMonth'
            if dayString == todayString:
                elementClass += ' today'

            code += '<span class="dayLabel{}">{}</span>\n'.format(elementClass, dayString)

            # Process the day if there is data
            if dd[j][i]:
                # Battery level
                dayArray = dd[j][i]
                chargeLevel = dayArray[-1]['charge_state']['battery_level']
                elementClass = ''
                #r = tt[j][i].tm_wday
                r = int(chargeLevel / 10)
                if r <= 5:
                   elementClass += ' charge{}'.format(r)
                code += '<div class="chargeLevel{}" style="height:{}%"></div>\n'.format(elementClass, chargeLevel)

                # Calculate total miles driven
                if o1 is None:
                    o1 = dayArray[0]['vehicle_state']['odometer']
                o0 = dayArray[-1]['vehicle_state']['odometer']
                delta_o = o0 - o1
                o1 = o0
                carDriven = delta_o > 1.0

                # day
                # temp = [d['climate_state']['outside_temp'] for d in dayArray]
                # temp = np.array(temp, dtype=np.float)
                # minTemp = np.nanmin(temp) * 9 / 5 + 32.0
                # maxTemp = np.nanmax(temp) * 9 / 5 + 32.0

                # If there was a charging event
                carCharged = any([d['charge_state']['charging_state'] == 'Charging' for d in dayArray])

                # Software version
                if s1 is None:
                    s1 = dayArray[0]['vehicle_state']['car_version']
                s0 = dayArray[-1]['vehicle_state']['car_version']
                if s0 != s1:
                    carUpdated = True
                else:
                    carUpdated = False
                s1 = s0

                # Icon bar using the information derived earlier
                def insertOrFadeIcon(cond, image):
                    appendix = ''
                    if cond or showFadeIcon:
                        if not cond and showFadeIcon:
                            appendix = ' fade'
                        return '<img class="icon{}" src="{}">\n'.format(appendix, image)
                    return ''
                code += '<div class="iconBar">\n'
                code += insertOrFadeIcon(carDriven, "blob/wheel.png")
                code += insertOrFadeIcon(carCharged, "blob/charge.png")
                code += insertOrFadeIcon(carUpdated, "blob/up.png")
                code += '</div>\n'

                # Lines of information
                code += '<div class="info">\n'
                code += '<span class="textInfo large">{}%</span>\n'.format(chargeLevel)
                code += '<span class="textInfo medium">{}</span>\n'.format(time.strftime('%-I:%M %p', tt[j][i]))
                code += '<span class="textInfo medium">{:+.1f} mi ({})</span>\n'.format(delta_o, len(dayArray))
                code += '<span class="textInfo medium">{:.1f} mi</span>\n'.format(o0)
                code += '</div>\n'

            code += '</div>\n'

    code += '</div>\n'
    code += '</body>\n'
    code += '</html>\n'

    return code
