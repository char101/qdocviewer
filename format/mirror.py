import threading
from functools import lru_cache
from queue import Empty, SimpleQueue
from threading import Thread
from time import gmtime, strftime
from urllib.parse import urljoin

import httpx
import orjson as json
import zstandard as zstd

from .. import DOCS_DIR, sqlite, term, utils
from . import logger
from .base import BaseFormat, Item


class WriterThread(Thread):
    """A writer thread to serialize write because MirrorFormat object is run by multiple threads by the web server."""

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
                if len(data) == 2:
                    path, updated = data
                    curr.execute('update cache set updated = ? where path = ?', (updated, path))
                else:
                    curr.execute('insert or replace into cache (path, status, headers, content, updated) values (?, ?, jsonb(?), ?, ?)', data)
            except Empty:
                pass
        conn.close()


class MirrorFormat(BaseFormat):
    """
    - only handles path that are relative to prefix
    - other resources should be treated just like directory doc accessing external resources
    """

    def __init__(self, name, params):
        super().__init__(name, params)

        url = params.get('url')
        assert url.endswith('/'), f'Invalid prefix: {url}'
        self.prefix = url
        self.path = (DOCS_DIR / name).mkdir_p()
        self.dbpath = self.path / 'cache.sqlite'
        self.start = params.get('start')
        self.index = params.get('index')  # index location on the remote

        self.props = {}
        self._init_db()

        # cannot use http2, only works with AsyncClient
        self.client = httpx.Client(limits=httpx.Limits(max_connections=5))
        self.queue = SimpleQueue()
        self.writer = WriterThread(self.dbpath, self.queue)
        self.writer.start()

    def _init_db(self):
        conn = sqlite.connect(self.dbpath, autocommit=True)
        curr = conn.cursor()
        curr.execute('create table if not exists prop (key text not null primary key, value blob not null)')
        curr.execute('create table if not exists cache (path text not null primary key, status int not null, headers jsonb not null, content blob, updated int not null, refresh int default 0 not null)')

        curr.execute('select key, value from prop')
        props = self.props
        for row in curr.fetchall():
            props[row[0]] = json.loads(row[1])
        conn.close()

    def get_prop(self, key, default=None):
        return self.props.get(key, default)

    def set_prop(self, key, value):
        conn = sqlite.connect(self.dbpath, autocommit=True)
        conn.execute('insert or replace into prop (key, value) values (?, ?)', (key, json.dumps(value)))
        self.props[key] = value
        conn.close()

    def get_index(self):
        if self.index:
            return self.process_index(self.index, self[self.index].content)
        return super().get_index()

    def stop(self):
        self.writer._stop = True

    @lru_cache(20)
    def __getitem__(self, path):
        local = threading.local()
        if not hasattr(local, 'conn'):
            local.conn = sqlite.connect(self.dbpath)
        conn = local.conn

        baseline = self.get_prop('baseline')

        for _path in self.generate_names(path):
            if row := conn.execute("select status, headers ->> '$.content-type' as content_type, headers ->> '$.location' as location, content, updated from cache where path = ?", (_path,)).fetchone():
                status, content_type, location, content, updated = row
                item = Item(zstd.decompress(content) if content else '', status=status, content_type=content_type or 'application/octet-stream', location=location, updated=updated)
                if baseline and (updated is None or updated < baseline):
                    return self._fetch(_path, item)
                # logger.warn('%s %s %s %s', term.blue('CACHE'), _path, status, content_type)
                return item

        return self._fetch(path)

    def _fetch(self, path, item=None):
        url = urljoin(self.prefix, path)

        # if item is given, do a if-modified-since request
        headers = {}
        if item and item.updated:
            headers['If-Modified-Since'] = strftime('%a, %d %b %Y %H:%M:%S GMT', gmtime(item.updated))

        time = utils.epoch()

        r = self.client.get(url, headers=headers)
        if r.status_code == 304:
            ic(url, r.status_code)
            self.queue.put((path, time))
            item.updated = time
            return item

        self.queue.put((
            path,
            r.status_code,
            json.dumps(dict(r.headers)),  # all keys in lower case
            zstd.compress(r.content),
            time,
        ))
        logger.warn('%s %s %s %s %s %s', term.yellow('FETCH'), url, r.http_version, term.gr(r.status_code, r.status_code == 200), r.headers.get('content-type'), r.headers.get('location'))

        return Item(r.content, status=r.status_code, content_type=r.headers.get('content-type', 'application/octet-stream'), location=r.headers.get('location'), updated=time)
