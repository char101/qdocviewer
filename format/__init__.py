import logging
import os
from importlib import import_module

from .. import DOCS_DIR

logger = logging.getLogger(__name__)


def get_format(name, params):
    path = params.get('path', name)
    if 'url' in params:
        return 'mirror'
    if os.path.splitext(path)[1] == '.zip' or os.path.exists(DOCS_DIR / f'{name}.zip'):
        return 'zipped'
    return 'directory'


def create_instance(name, params, format):
    module = import_module('.' + format, __name__)
    Class = getattr(module, f'{format.title()}Format')
    return Class(name, params)
