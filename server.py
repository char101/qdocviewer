from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlparse

from . import mime_db, qt


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        doc = self.server.doc
        if self.path.startswith('/https://') or self.path.startswith('/http://'):
            path = self.path.lstrip('/')
        else:
            path = urlparse(self.path).path.lstrip('/')  # remove query from path

        if not doc.format == 'mirror' and path == '':
            path = 'index.html'

        try:
            item = doc[path]
        except KeyError:
            ic('not found', path)
            self._send_content(f'Path {path} not found in {doc.path}', status=HTTPStatus.NOT_FOUND)
            return

        status = item.status or HTTPStatus.OK
        mime = item.content_type or mime_db.mimeTypeForFile(item.name, qt.QMimeDatabase.MatchMode.MatchExtension).name()

        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', len(item.content))
        self.send_header('Access-Control-Allow-Origin', '*')
        if status in (301, 302):
            self.send_header('Location', self._fix_redirect(item.location, doc))
        elif status == 200:
            self.send_header('Cache-Control', 'max-age=604800')  # make js/css cached by the client
        self.end_headers()

        self.wfile.write(item.content)

    # disable request logging
    def log_message(self, format, *args):
        pass

    def _send_content(self, content, status=HTTPStatus.OK, type='text/plain'):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def _fix_redirect(self, url, doc):
        # redirect without domain
        if url.startswith('/'):
            return url

        # redirect with same domain
        if url.startswith(doc.prefix):
            assert doc.prefix[-1] == '/'
            return url[len(doc.prefix) - 1 :]

        if url.startswith('http://') or url.startswith('https://'):
            return self.server.prefix + url

        raise Exception('Invalid redirect: ' + url)


class HttpServer(ThreadingHTTPServer):
    def __init__(self, doc):
        super().__init__(('127.0.0.1', 0), RequestHandler)
        self.doc = doc  # used by RequestHandler
        self.thread = Thread(target=self.serve_forever)

    @property
    def prefix(self):
        return f'http://127.0.0.1:{self.server_port}/'

    def start(self):
        self.thread.start()

    def stop(self):
        self.shutdown()
