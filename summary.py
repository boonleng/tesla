#!/usr/local/bin/python

__version__ = '1.0'

import glob
import datetime
import argparse

import getStat

boolColor = 135
numberColor = 82
stringColor = 228

def showVariable(variable, value, color=82):
    print('\033[38;5;214m{}\033[m = \033[38;5;{}m{}\033[m'.format(variable, color, value))

def showKeyValue(obj, key, unit=""):
    value = obj[key]
    if isinstance(value, bool):
        color = boolColor
    elif isinstance(value, (int, float)):
        color = numberColor
    else:
        color = stringColor
    showVariable(key, '{}{}'.format(value, unit), color)

def prettyAgeString(timestamp, showSeconds=True):
    now = datetime.datetime.now()
    age = now - timestamp
    ageString = ''
    d = age.days
    if d > 0:
        ageString += '{}'.format(d)
        if d > 1:
            ageString += 's'
    s = age.seconds
    m = int(s / 60)
    if m > 0:
        if len(ageString):
            ageString += ' '
        ageString += '{} minute'.format(m)
        if m > 1:
            ageString += 's'
    if showSeconds:
        s -= m * 60
        if s > 0:
            if len(ageString):
                ageString += ' '
            ageString += '{} second'.format(s)
            if s > 1:
                ageString += 's'
    if len(ageString):
        ageString += ' ago'
    else:
        ageString = 'now'
    return '{} ({})'.format(t.strftime('%Y%m%d-%H%M%S'), ageString)

#
#     M  A  I  N
#

if __name__ == '__main__':
    # First things first, parse all the arguments
    usage = '''
        summary.py [options]

        Tesla Data Log Summary
        '''
    parser = argparse.ArgumentParser(prog='Summary', usage=usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-r', default=False, action="store_true", help='shows the real-time summary, instant retrieval')
    parser.add_argument('-v', default=0, action='count', help='increase verbosity')
    args = parser.parse_args()

    if args.r:
        data = getStat.requestData()
        if data is None:
            print('Vehicle is sleeping.')
            exit(0)
    else:
        folders = glob.glob('{}/2*'.format(getStat.dataLogHome))
        folders.sort()
        dataLogs = glob.glob('{}/*.json'.format(folders[-1]))
        dataLogs.sort()
        filename = dataLogs[-1]
        print('From \033[38;5;228m{}\033[m'.format(filename))
        data = getStat.objFromFile(filename)

    if args.v:
        print(data)

    t = datetime.datetime.fromtimestamp(data['charge_state']['timestamp'] / 1000)
    showVariable('timestamp', prettyAgeString(t))
    fullRange = data['charge_state']['battery_range'] / data['charge_state']['battery_level'] * 100.0
    showVariable('derived_battery_health', '{:.1f} mi'.format(fullRange))
    showKeyValue(data['charge_state'], 'ideal_battery_range', ' mi')
    showKeyValue(data['charge_state'], 'est_battery_range', ' mi')
    showKeyValue(data['charge_state'], 'battery_range', ' mi')
    showKeyValue(data['charge_state'], 'battery_level', '%')
    showKeyValue(data['climate_state'], 'is_climate_on')
    tempC = data['climate_state']['inside_temp']
    showVariable('inside_temp', '{:.1f}°C / {:.1f}°F'.format(tempC, tempC * 9 / 5))
    showKeyValue(data['charge_state'], 'charging_state')
    if data['charge_state']['charging_state'] == "Charging":
        showKeyValue(data['charge_state'], 'charger_power', ' kW')
        showKeyValue(data['charge_state'], 'charger_voltage', ' V')
        showKeyValue(data['charge_state'], 'charger_actual_current', ' A')
    showKeyValue(data['vehicle_state'], 'is_user_present')
    showKeyValue(data['vehicle_state'], 'sentry_mode')
