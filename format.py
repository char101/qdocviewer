import orjson as json
from zipfile_zstd import ZipFile

from . import DOCS_DIR, utils


class Doc:
    def has_index(self):
        for file in ('searchindex.js', 'genindex.html', 'index.json'):
            if file in self:
                return True
        return False

    def get_index(self):
        for file in ('searchindex.js', 'genindex.html', 'index.json'):
            if file in self:
                match file:
                    case 'searchindex.js':
                        return utils.extract_searchindex(self[file])
                    case 'genindex.html':
                        return utils.extract_genindex(self[file])
                    case 'index.json':
                        return json.loads(self[file])


class DirectoryDoc(Doc):
    def __init__(self, path, prefix=None):
        self.path = path
        if prefix:
            self.path = self.path / prefix

    def __contains__(self, name):
        return (self.path / name).exists()

    def __getitem__(self, name):
        return (self.path / name).read_bytes()


class ZippedDoc(Doc):
    def __init__(self, path, prefix=None):
        self.path = path
        self.prefix = (prefix.strip('/') + '/') if prefix else ''
        self.zf = ZipFile(path)

    def __del__(self):
        self.zf.close()

    def __contains__(self, name):
        try:
            with self.zf.open(self.prefix + name):
                return True
        except KeyError:
            return False

    def __getitem__(self, name):
        try:
            with self.zf.open(self.prefix + name) as f:
                return f.read()
        except KeyError:
            if not name.endswith('.html'):
                with self.zf.open(self.prefix + name + '.html') as f:
                    return f.read()


def create_instance(path, **kwargs):
    path = DOCS_DIR / path
    if path.isdir():
        return DirectoryDoc(path, **kwargs)
    if path.ext == '.zip':
        return ZippedDoc(path, **kwargs)
    raise Exception('Unknown format: ' + path)
