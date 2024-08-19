from .. import DOCS_DIR
from .base import BaseFormat, Item


class DirectoryFormat(BaseFormat):
    def __init__(self, name, params):
        super().__init__(name, params)
        self.path = DOCS_DIR / name
        if dir := params.get('dir'):
            self.path = self.path / dir
        if prefix := params.get('prefix'):
            self.path = self.path / prefix
        self.start = params.get('start')

    def __getitem__(self, name):
        if name.startswith('https://') or name.startswith('http://'):
            return self.get_external_resource(name)

        for name in self.generate_names(name):
            try:
                path = self.path / name
                content = path.read_bytes()
                return Item(name, content=content, updated=path.mtime)
            except FileNotFoundError:
                pass
        raise KeyError(f'Cannot find {name} in {self.path}')
