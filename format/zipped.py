from datetime import datetime

from zipfile_zstd import ZipFile

from .. import DOCS_DIR
from .base import BaseFormat, Item


class ZippedFormat(BaseFormat):
    def __init__(self, name, params):
        super().__init__(name, params)
        self.path = DOCS_DIR / params['path'] if 'path' in params else DOCS_DIR / f'{name}.zip'
        self.prefix = (params['prefix'].strip('/') + '/') if 'prefix' in params else ''
        self.zf = ZipFile(self.path)
        self.start = params.get('start')

    def __del__(self):
        self.zf.close()

    def __getitem__(self, name):
        for name in self.generate_names(name):
            try:
                path = self.prefix + name
                with self.zf.open(path) as f:
                    content = f.read()
                info = self.zf.getinfo(path)
                return Item(content=content, updated=int(datetime(*info.date_time).timestamp()))
            except KeyError:
                pass
        raise KeyError(f'Cannot find {name} in {self.path}')
