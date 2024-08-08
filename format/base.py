import os
from functools import cached_property

import orjson as json
import polars as pl
from recordclass import dataobject

from .. import utils

GLOBAL_WHITELIST = {
    'cdnjs.cloudflare.com',
    'unpkg.com',
    'cdn.jsdelivr.net',
    'ajax.googleapis.com',
    'raw.githubusercontent.com',
    'fonts.googleapis.com',
    'fonts.gstatic.com',
}


class Item(dataobject):
    content: bytes
    status: int = None
    content_type: str = None
    location: str = None
    updated: int = None


class BaseFormat:
    def __init__(self, name, params):
        self.name = name
        self.whitelist = params.get('whitelist', set())
        self.reset_counter()

    @cached_property
    def format(self):
        return self.__class__.__name__[:-6].lower()

    def generate_names(self, name):
        """Generate alternative names for name"""
        yield name
        yield name + '.html'
        yield name.rstrip('/') + '/index.html' if name else 'index.html'

    def reset_counter(self):
        self.counter = {'fetch': 0, 'cache': 0, 'refresh': 0, 'block': 0}

    def process_index(self, path, content):
        match os.path.basename(path):
            case 'searchindex.js':
                return utils.extract_searchindex(content, path)
            case 'genindex.html':
                return utils.extract_genindex(content, path)
            case 'index.json':
                symbols, locations = json.loads(content)
                df = pl.DataFrame({'symbol': symbols, 'location': locations})
                df.sort('symbol')
                return df
            case 'index.hhk':
                return utils.extract_hhk(content)

    def get_index(self):
        match self.name:
            case 'mdn':
                df = pl.DataFrame(json.loads(self['en-US/search-index.json'].content)).rename({'title': 'symbol', 'url': 'location'})
                df.sort('symbol')
                return df
            case 'autohotkey':
                data = json.loads(self['static/source/data_index.js'].content[12:-3])
                df = pl.DataFrame(data, orient='row').rename(dict(column_0='symbol', column_1='location'))
                df.sort('symbol')
                return df

        for file in ('searchindex.js', 'genindex.html', 'index.json', 'index.hhk'):
            try:
                item = self[file]
                if item.status == 200 or item.status is None:
                    return self.process_index(file, item.content)
                break
            except KeyError:
                continue

    def is_whitelisted(self, url):
        host = url.host()
        return host in GLOBAL_WHITELIST or host in self.whitelist

    def stop(self):
        pass
