import os
import json
import requests
import configparser

import foundation

site = 'owner-api.teslamotors.com'
rcFile = os.path.expanduser('~/.teslarc')

def getConfig():
    if not os.path.exists(rcFile):
        foundation.logger.info('No configuration file. Setting up ...')
        try:
            username = input('Enter username: ')
            if len(username) == 0:
                foundation.logger.info('Setup aborted. No username provided.')
                return None
        except KeyboardInterrupt:
            foundation.logger.exception('Setup aborted. User aborted the setup.')
            return None

        import getpass
        import keyring

        password = keyring.get_password(site, username)
        if not password:
            password = getpass.getpass('Enter password: ')
            if not password:
                foundation.logger.info('Setup aborted. No password provided.')
                return None
            keyring.set_password(site, username, password)
            foundation.logger.info('Password saved to Keychain Access')

        # Retrieve a token using the login provided
        url = 'https://{}/oauth/token'.format(site)
        payload = {
            'grant_type': 'password',
            'client_id': '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384',
            'client_secret': 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3',
            'email': username,
            'password': password
        }
        headers = {
            'Host': site,
            'User-Agent': 'Learning',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            foundation.logger.exception('Unable to retrieve token. r = {}'.format(r.status_code))
            return None
        token = r.json()

        # Retrieve a list of vehicles
        url = 'https://owner-api.teslamotors.com/api/1/vehicles'
        headers = {
            'Authorization': 'Bearer {}'.format(token['access_token'])
        }
        r = requests.get(url, headers=headers)
        cars = []
        if r.status_code == 200:
            cars = r.json()['response']
        else:
            foundation.logger.exception('Unable to retrieve list of vehicles.')

        # Save username and token into the configuration
        config = configparser.ConfigParser()
        config.add_section('user')
        config.add_section('token')
        config['user'] = {'username': username}
        config['token'] = token
        if len(cars):
            for car in cars:
                key = car['vin']
                config.add_section(key)
                config[key] = {'id': car['id'],
                               'vid': car['vehicle_id'],
                               'name': car['display_name']}
        with open(rcFile, 'w') as fid:
            config.write(fid)

        foundation.logger.info('Config setup complete')

    # Make a config and load the configuration
    config = configparser.ConfigParser()
    try:
        config.read(rcFile)
    except configparser.ParsingError as e:
        foundation.logger.exception('Bad config file.')
        raise ConfigError from e

    # Assess the completeness
    if not all(sec in config.sections() for sec in ['user', 'token']):
        foundation.logger.exception('Bad config file. Try removing it and rerun this script.')
        return None

    cars = []
    for sec in config.sections():
        if sec not in ['user', 'token']:
            cars.append(dict(config[sec]))
    return {'username':config['user']['username'], 'token':dict(config['token']), 'cars':cars}
