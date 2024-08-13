import logging
from importlib import import_module

from .. import DOCS_DIR

logger = logging.getLogger(__name__)


def get_format(name, params):
    if 'url' in params:
        return 'mirror'

    path = DOCS_DIR / params.get('path', name)
    if path.suffix == '.zip':
        return 'zipped'
    if path.isdir():
        return 'directory'
    if path.with_suffix('.zip').exists():
        return 'zipped'


def create_instance(name, params, format):
    module = import_module('.' + format, __name__)
    Class = getattr(module, f'{format.title()}Format')
    return Class(name, params)
