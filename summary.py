#!/usr/local/bin/python

__version__ = '1.0.1'

import os
import glob
import time
import argparse

import tesla

boolColor = 135
numberColor = 82
stringColor = 228

def showVariable(variable, value, color=numberColor):
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
    now = time.time()
    age = now - timestamp
    ageString = ''
    d = int(age / 86400)
    if d > 0:
        ageString += '{} day'.format(d)
        if d > 1:
            ageString += 's'
    s = age - d * 86400
    h = int(s / 3600)
    if h > 0:
        if len(ageString):
            ageString += ' '
        ageString += '{} hour'.format(h)
        if h > 1:
            ageString += 's'
    m = int((s - h * 3600) / 60)
    if m > 0:
        if len(ageString):
            ageString += ' '
        ageString += '{} minute'.format(m)
        if m > 1:
            ageString += 's'
    if showSeconds:
        s -= (h * 3600 + m * 60)
        if s > 0:
            if len(ageString):
                ageString += ' '
            ageString += '{:.0f} second'.format(s)
            if s > 1:
                ageString += 's'
    if len(ageString):
        ageString += ' ago'
    else:
        ageString = 'now'
    return '{} ({})'.format(time.strftime('%Y%m%d-%H%M%S', time.localtime(timestamp)), ageString)

def c2f(c):
    if c is None:
        return None
    return c * 1.8 + 32

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

    if args.v:
        tesla.showInfoMessages()

    if args.r:
        data = tesla.requestData()
        if data is None:
            print('Vehicle is sleeping.')
            exit(0)
        print('From the vehicle directly.')
    else:
        folders = glob.glob('{}/2*'.format(tesla.dataLogHome))
        folders.sort()
        dataLogs = glob.glob('{}/*.json'.format(folders[-1]))
        dataLogs.sort()
        filename = dataLogs[-1]
        print('From \033[38;5;{}m{}\033[m'.format(stringColor, filename))
        data = tesla.objFromFile(filename)

    if args.v:
        import pprint
        pprint.pprint(data)

    t = data['charge_state']['timestamp'] / 1000
    showVariable('timestamp', prettyAgeString(t))
    fullRange = data['charge_state']['battery_range'] / data['charge_state']['battery_level'] * 100.0
    showVariable('projected_full_battery_range', '{:.1f} mi'.format(fullRange), 51)   # my projected range at 100% charge
    showKeyValue(data['charge_state'], 'ideal_battery_range', ' mi')                  # ideal range without degradation
    showKeyValue(data['charge_state'], 'est_battery_range', ' mi')                    # range estimated from recent driving
    showKeyValue(data['charge_state'], 'battery_range', ' mi')                        # current battery range
    showKeyValue(data['charge_state'], 'battery_level', '%')                          # current battery state of charge
    showKeyValue(data['climate_state'], 'is_climate_on')                              # climate control
    tc = data['climate_state']['inside_temp']                                         # interior temperature
    if tc is None:
        showVariable('inside_temp', 'None', boolColor)                                # show temperature in C & F
    else:
        showVariable('inside_temp', '{:.1f}°C / {:.1f}°F'.format(tc, c2f(tc)))        # show temperature in C & F
    tc = data['climate_state']['outside_temp']                                        # exterior temperature
    if tc is None:
        showVariable('outside_temp', 'None', boolColor)                               # show temperature in C & F
    else:
        showVariable('outside_temp', '{:.1f}°C / {:.1f}°F'.format(tc, c2f(tc)))       # show temperature in C & F
    showKeyValue(data['charge_state'], 'charging_state')                              # charge state (disconnected, charging, etc.)
    if data['charge_state']['charging_state'] == "Charging":
        showKeyValue(data['charge_state'], 'charger_power', ' kW')                    # charge power
        showKeyValue(data['charge_state'], 'charger_voltage', ' V')                   # charge voltage
        showKeyValue(data['charge_state'], 'charger_actual_current', ' A')            # charge current
        showKeyValue(data['charge_state'], 'charge_rate', ' mi/hr')                   # charge rate at mi/hr
    showKeyValue(data['vehicle_state'], 'is_user_present')                            # the presence of a user
    showKeyValue(data['vehicle_state'], 'sentry_mode')                                # activation of sentry mode
    showKeyValue(data['vehicle_state'], 'locked')                                     # vehicle lock
    showKeyValue(data['vehicle_state'], 'odometer', ' mi')                            # odometer
    showKeyValue(data['vehicle_state'], 'car_version')                                # software version
