import configparser
from os import path

from core import consts

_config = configparser.ConfigParser()
_config.read(path.join(consts.cwd(), 'config.ini'))


def get_config():
    return _config
