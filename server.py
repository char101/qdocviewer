from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from . import mime_db, qt


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        doc = self.server.doc
        path = urlparse(self.path).path.lstrip('/')

        if path not in doc:
            if not path.endswith('.html') and (path + '.html') in doc:
                path = path + '.html'
            elif (path.rstrip('/') + '/index.html') in doc:
                path = path.rstrip('/') + '/index.html'
            else:
                self.send_content(f'Path {path} not found in {doc.path}', status=HTTPStatus.NOT_FOUND)
                return

        item = doc[path]
        status = item.status or HTTPStatus.OK
        mime = item.content_type or mime_db.mimeTypeForFile(path, qt.QMimeDatabase.MatchMode.MatchExtension).name()

        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', len(item.content))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'max-age=604800')  # make js/css cached by the client
        self.end_headers()

        self.wfile.write(item.content)

    # disable request logging
    def log_message(self, format, *args):
        pass

    def send_content(self, content, status=HTTPStatus.OK, type='text/plain'):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', type)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)


class Thread(qt.QThread):
    def __init__(self, server):
        super().__init__()
        self._server = server

    def run(self):
        self._server.serve_forever()


class HttpServer(ThreadingHTTPServer):
    def __init__(self, doc):
        super().__init__(('127.0.0.1', 0), RequestHandler)
        self.doc = doc

    @property
    def prefix(self):
        return f'http://127.0.0.1:{self.server_port}/'

    def start(self):
        self._thread = thread = Thread(self)
        thread.start()

    def stop(self):
        self.shutdown()
