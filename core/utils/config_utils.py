import configparser
from os import path

import dateutil.tz

from core import consts

_config = configparser.ConfigParser()
_config.read(path.join(consts.cwd(), 'config.ini'))


def get_config():
    return _config


def gettz():
    return dateutil.tz.gettz(_config['global']['tz'])
