import os
import keyring
import getpass
import configparser

import foundation

RC_FILE = os.path.expanduser('~/.teslarc')
SITE = 'owner-api.teslamotors.com'

def _get_rc():
    if not os.path.exists(RC_FILE):
        foundation.logger.info('No configuration file. Setting up ...')
        try:
            username = input('Enter username: ')
        except KeyboardInterrupt:
            foundation.logger.exception('Setup aborted.')
            return None

        config = configparser.ConfigParser()
        config.add_section('user')
        config['user'] = {'username': username}

        with open(RC_FILE, 'w') as fid:
            config.write(fid)

        if not keyring.get_password(SITE, username):
            password = getpass.getpass('Enter password: ')
            if not password:
                foundation.logger.info('User did not enter a password.')
                return None
            keyring.set_password(SITE, username, password)
            foundation.logger.info('Password saved to Keychain Access')

        foundation.logger.info('Config setup complete')


    config = configparser.ConfigParser()
    try:
        config.read(RC_FILE)
    except configparser.ParsingError as e:
        foundation.logger.exception('Bad config file.')
        raise ConfigError from e

    if 'user' not in config.sections():
        return None
    config = dict(config['user'])
    return config

config = _get_rc();

# print(config['username'])
# print(keyring.get_password(SITE, config['username']))
