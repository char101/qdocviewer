import logging
from importlib import import_module

logger = logging.getLogger(__name__)


def get_format(name, params):
    if 'url' in params:
        return 'mirror'
    if 'zip' in params:
        return 'zipped'
    return 'directory'


def create_instance(name, params, format):
    module = import_module('.' + format, __name__)
    Class = getattr(module, f'{format.title()}Format')
    return Class(name, params)
