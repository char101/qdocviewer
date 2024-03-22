import sqlite3
from datetime import datetime
from queue import Empty, SimpleQueue
from threading import Thread
from urllib.parse import urljoin

import httpx
import orjson as json
import zstandard as zstd
from recordclass import dataobject
from zipfile_zstd import ZipFile

from . import DOCS_DIR, utils


class Item(dataobject):
    content: bytes
    status: int = None
    content_type: str = None


class Doc:
    threading = True

    def get_index(self):
        for file in ('searchindex.js', 'genindex.html', 'index.json'):
            if file in self:
                match file:
                    case 'searchindex.js':
                        return utils.extract_searchindex(self[file].content)
                    case 'genindex.html':
                        return utils.extract_genindex(self[file].content)
                    case 'index.json':
                        return json.loads(self[file].content)


class DirectoryDoc(Doc):
    def __init__(self, path, prefix=None):
        self.path = path
        if prefix:
            self.path = self.path / prefix

    def __contains__(self, name):
        return (self.path / name).exists()

    def __getitem__(self, name):
        return Item((self.path / name).read_bytes())


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
                return Item(f.read())
        except KeyError:
            if not name.endswith('.html'):
                with self.zf.open(self.prefix + name + '.html') as f:
                    return Item(f.read())


class WriterThread(Thread):
    def __init__(self, queue, conn):
        super().__init__()
        self._queue = queue
        self._conn = conn
        self._curr = conn.cursor()

    def run(self):
        queue = self._queue
        curr = self._curr
        while True:
            try:
                data = queue.get(timeout=1)
                curr.execute('insert or ignore into cache (path, status, headers, content_type, content, created) values (?, ?, ?, ?, ?, ?)', data)
            except Empty:
                pass


class CachedDoc(Doc):
    """
    - only handles path that are relative to prefix
    - other resources should be treated just like directory doc accessing external resources
    """

    threading = False

    def __init__(self, name, prefix):
        conn = sqlite3.connect(DOCS_DIR / name, check_same_thread=False, autocommit=True)
        conn.executescript('pragma journal_mode = WAL; pragma synchronous = off; pragma temp_store = memory;')
        conn.execute('create table if not exists cache (path text not null primary key, status int not null, headers text, content_type text, content text, created int not null)')
        self.conn = conn

        assert prefix.endswith('/'), f'Invalid prefix: {prefix}'
        self.prefix = prefix

        self.client = None
        self.queue = None
        self.writer = None

    def __contains__(self, path):
        try:
            row = self.conn.execute('select status from cache where path = ?', (path,)).fetchone()
        except Exception as err:
            print(f'error={err} path={path}')
            raise
        return row is None or row[0] == 200

    def __getitem__(self, path):
        if row := self.conn.execute('select status, content_type, content from cache where path = ?', (path,)).fetchone():
            status, content_type, content = row
            assert content is not None, path
            # ic('cached', path, status, content_type)
            return Item(zstd.decompress(content), status=status, content_type=content_type)
        return self._fetch(path)

    def _fetch(self, path):
        url = urljoin(self.prefix, path)

        if not self.client:
            self.client = httpx.Client(limits=httpx.Limits(max_connections=5))
            self.queue = SimpleQueue()
            self.writer = WriterThread(self.queue, self.conn)
            self.writer.start()

        ic('fetching', url)
        r = self.client.get(url)
        self.queue.put((path, r.status_code, json.dumps(dict(r.headers)), r.headers['content-type'], zstd.compress(r.content), int(datetime.now().timestamp())))
        ic(r.status_code, r.headers['Content-Type'])
        return Item(r.content, status=r.status_code, content_type=r.headers['content-type'])


def create_instance(path, **kwargs):
    path = DOCS_DIR / path
    if path.isdir():
        return DirectoryDoc(path, **kwargs)
    if path.ext == '.zip':
        return ZippedDoc(path, **kwargs)
    if path.ext == '.sqlite':
        return CachedDoc(path, **kwargs)

    raise Exception('Unknown format: ' + path)
