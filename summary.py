#!/usr/local/bin/python

__version__ = '1.0'

import glob
import datetime
import argparse

import getStat

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

def c2f(c):
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

    if args.r:
        data = getStat.requestData()
        if data is None:
            print('Vehicle is sleeping.')
            exit(0)
        print('From the vehicle directly.')
    else:
        folders = glob.glob('{}/2*'.format(getStat.dataLogHome))
        folders.sort()
        dataLogs = glob.glob('{}/*.json'.format(folders[-1]))
        dataLogs.sort()
        filename = dataLogs[-1]
        print('From \033[38;5;{}m{}\033[m'.format(stringColor, filename))
        data = getStat.objFromFile(filename)

    if args.v:
        import pprint
        pprint.pprint(data)

    t = datetime.datetime.fromtimestamp(data['charge_state']['timestamp'] / 1000)
    showVariable('timestamp', prettyAgeString(t))
    fullRange = data['charge_state']['battery_range'] / data['charge_state']['battery_level'] * 100.0
    showVariable('projected_full_battery_range', '{:.1f} mi'.format(fullRange), 51)   # my projected range at 100% charge
    showKeyValue(data['charge_state'], 'ideal_battery_range', ' mi')                  # ideal range without degradation
    showKeyValue(data['charge_state'], 'est_battery_range', ' mi')                    # range estimated from recent driving
    showKeyValue(data['charge_state'], 'battery_range', ' mi')                        # current battery range
    showKeyValue(data['charge_state'], 'battery_level', '%')                          # current battery state of charge
    showKeyValue(data['climate_state'], 'is_climate_on')                              # climate control
    tc = data['climate_state']['inside_temp']                                         # interior temperature
    showVariable('inside_temp', '{:.1f}°C / {:.1f}°F'.format(tc, c2f(tc)))            # show temperature in C & F
    tc = data['climate_state']['outside_temp']                                        # exterior temperature
    showVariable('outside_temp', '{:.1f}°C / {:.1f}°F'.format(tc, c2f(tc)))           # show temperature in C & F
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
