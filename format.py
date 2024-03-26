import logging
import os
import sqlite3
import threading
from datetime import datetime
from queue import Empty, SimpleQueue
from threading import Thread
from urllib.parse import urljoin, urlparse

import httpx
import orjson as json
import polars as pl
import zstandard as zstd
from recordclass import dataobject
from zipfile_zstd import ZipFile

from . import DOCS_DIR, sqlite, term, utils

logger = logging.getLogger(__name__)


class Item(dataobject):
    content: bytes
    status: int = None
    content_type: str = None
    location: str = None


class Doc:
    def get_index(self):
        for file in ('searchindex.js', 'genindex.html', 'index.json'):
            if file in self:
                item = self[file]
                if item.status == 200 or item.status is None:
                    match file:
                        case 'searchindex.js':
                            return utils.extract_searchindex(item.content)
                        case 'genindex.html':
                            return utils.extract_genindex(item.content)
                        case 'index.json':
                            symbols, locations = json.loads(item.content)
                            df = pl.DataFrame({'symbol': symbols, 'location': locations})
                            df.sort('symbol')
                            return df

    def set_whitelist(self, domains):
        self.whitelist_domains = domains

    def is_whitelisted(self, url):
        return hasattr(self, 'whitelist_domains') and url.host() in self.whitelist_domains

    def stop(self):
        pass


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
    def __init__(self, dbpath, queue):
        super().__init__()
        self._dbpath = dbpath
        self._queue = queue
        self._stop = False

    def run(self):
        conn = sqlite.connect(self._dbpath, autocommit=True)
        curr = conn.cursor()
        queue = self._queue
        while not self._stop:
            try:
                data = queue.get(timeout=1)
                curr.execute('insert or ignore into cache (path, status, headers, content, created) values (?, ?, jsonb(?), ?, ?)', data)
            except Empty:
                pass
        conn.close()


class CachedDoc(Doc):
    """
    - only handles path that are relative to prefix
    - other resources should be treated just like directory doc accessing external resources
    """

    def __init__(self, name, url):
        assert url.endswith('/'), f'Invalid prefix: {url}'
        self.prefix = url

        path = DOCS_DIR.joinpath(name).mkdir_p()
        self.path = path
        self.dbpath = path / 'cache.sqlite'

        conn = sqlite.connect(self.dbpath)
        conn.execute('create table if not exists cache (path text not null primary key, status int not null, headers jsonb not null, content text, created int not null)')
        self.notfound = set(row[0] for row in conn.execute('select path from cache where status = 404').fetchall())
        conn.close()

        # cannot use http2, only works with AsyncClient
        self.client = httpx.Client(limits=httpx.Limits(max_connections=5))
        self.queue = SimpleQueue()
        self.writer = WriterThread(self.dbpath, self.queue)
        self.writer.start()

    def stop(self):
        self.writer._stop = True

    def __contains__(self, path):
        return path not in self.notfound

    def __getitem__(self, path):
        local = threading.local()
        if not hasattr(local, 'conn'):
            local.conn = sqlite.connect(self.dbpath)
        conn = local.conn

        if row := conn.execute("select status, headers ->> '$.content-type' as content_type, headers ->> '$.location' as location, content from cache where path = ?", (path,)).fetchone():
            status, content_type, location, content = row
            # logger.warn('%s %s %s %s', term.blue('CACHE'), path, status, content_type)
            return Item(zstd.decompress(content) if content else '', status=status, content_type=content_type or 'application/octet-stream', location=location)

        return self._fetch(path)

    def _fetch(self, path):
        url = urljoin(self.prefix, path)

        # ic('fetching', url)
        r = self.client.get(url)
        self.queue.put((
            path,
            r.status_code,
            json.dumps(dict(r.headers)),  # all keys in lower case
            zstd.compress(r.content),
            int(datetime.now().timestamp()),
        ))
        logger.warn('%s %s %s %s %s %s', term.yellow('FETCH'), url, r.http_version, term.gr(r.status_code, r.status_code == 200), r.headers.get('content-type'), r.headers.get('location'))

        if r.status_code == 404:
            self.notfound.add(path)

        return Item(r.content, status=r.status_code, content_type=r.headers.get('content-type', 'application/octet-stream'), location=r.headers.get('location'))


def get_type(path, params):
    if 'url' in params:
        return CachedDoc
    if os.path.splitext(path)[1] == '.zip':
        return ZippedDoc
    if os.path.isdir(os.path.join(DOCS_DIR, path)):
        return DirectoryDoc
    raise Exception('Unknown format: ' + path)


def create_instance(path, params):
    whitelist = params.pop('whitelist', None)

    doc = get_type(path, params)(DOCS_DIR / path, **params)

    if whitelist:
        doc.set_whitelist(whitelist)

    return doc
