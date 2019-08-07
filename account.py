import os
import json
import keyring
import getpass
import requests
import configparser

import foundation

RC_FILE = os.path.expanduser('~/.teslarc')
SITE = 'owner-api.teslamotors.com'

def _get_rc():
    if not os.path.exists(RC_FILE):
        foundation.logger.info('No configuration file. Setting up ...')
        try:
            username = input('Enter username: ')
            if len(username) == 0:
                foundation.logger.info('Setup aborted. No username provided.')
                return None
        except KeyboardInterrupt:
            foundation.logger.exception('Setup aborted. User aborted the setup.')
            return None

        password = keyring.get_password(SITE, username)
        if not password:
            password = getpass.getpass('Enter password: ')
            if not password:
                foundation.logger.info('Setup aborted. No password provided.')
                return None
            keyring.set_password(SITE, username, password)
            foundation.logger.info('Password saved to Keychain Access')

        # Retrieve a token using the login provided
        url = 'https://{}/oauto/token'.format(SITE)
        payload = {
            'grant_type': 'password',
            'client_id': '81527cff06843c8634fdc09e8ac0abefb46ac849f38fe1e431c2ef2106796384',
            'client_secret': 'c7257eb71a564034f9419ee651c7d0e5f7aa6bfbd18bafb5c5c033b093bb2fa3',
            'email': username,
            'password': password
        }
        headers = {
            'Host': SITE,
            'User-Agent': 'Learning',
            'Content-Type': 'application/json'
        }
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code != 200:
            foundation.logger.exception('Unable to retrieve token.')
            return None
        token = r.json()

        # Save username and token into the configuration
        config = configparser.ConfigParser()
        config.add_section('user')
        config.add_section('token')
        config['user'] = {'username': username}
        config['token'] = token
        with open(RC_FILE, 'w') as fid:
            config.write(fid)

        foundation.logger.info('Config setup complete')

    # Make a config and load the configuration
    config = configparser.ConfigParser()
    try:
        config.read(RC_FILE)
    except configparser.ParsingError as e:
        foundation.logger.exception('Bad config file.')
        raise ConfigError from e

    # Assess the completeness
    if not all(sec in config.sections() for sec in ['user', 'token']):
        foundation.logger.exception('Bad config file. Try removing it and rerun this script.')
        return None
    return {'username':config['user']['username'], 'token':dict(config['token'])}

config = _get_rc();

# print(config['username'])
# print(config['token'])
# print(keyring.get_password(SITE, config['username']))
