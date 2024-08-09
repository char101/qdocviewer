from .. import DOCS_DIR
from .base import BaseFormat, Item


class DirectoryFormat(BaseFormat):
    def __init__(self, name, params):
        super().__init__(name, params)
        self.path = params.get('path', DOCS_DIR / name)
        if prefix := params.get('prefix'):
            self.path = self.path / prefix

    def __getitem__(self, name):
        for name in self.generate_names(name):
            try:
                path = self.path / name
                content = path.read_bytes()
                return Item(name, content=content, time=path.mtime)
            except FileNotFoundError:
                pass
        raise KeyError(f'Cannot find {name} in {self.path}')
