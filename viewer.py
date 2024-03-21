from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import format, mime_db, qt
from .index import Widget as IndexWidget


class WebEngineView(qt.QWebEngineView):
    prevClicked = qt.Signal()
    nextClicked = qt.Signal()
    middleClicked = qt.Signal()
    ctrlLeftClicked = qt.Signal()

    def __init__(self, page):
        super().__init__(page)
        # self.focusProxy().installEventFilter(self)

    # def eventFilter(self, source, event):
    #     if self.focusProxy() == source and event.type() == qt.QEvent.MouseButtonPress:
    #         match event.button():
    #             case Qt.LeftButton:
    #                 if event.modifiers() & Qt.ControlModifier:
    #                     self.ctrlLeftClicked.emit()
    #                     return True
    #             case Qt.XButton1:
    #                 self.nextClicked.emit()
    #                 return True
    #             case Qt.XButton2:
    #                 self.prevClicked.emit()
    #                 return True
    #             case Qt.MiddleButton:
    #                 self.middleClicked.emit()
    #                 return True
    #     return super().eventFilter(source, event)


class Interceptor(qt.QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__(parent)
        self._doc = parent.parent()._doc

    def interceptRequest(self, info):
        url = info.requestUrl()
        match url.scheme():
            case 'https':
                ic('blocked', url)
                info.block(True)
            case 'http':
                if url.host() != '127.0.0.1':
                    ic('blocked', url)
                    info.block(True)
            case 'file':
                ic('blocked', url)
                info.block(True)
            case 'data':
                pass
            case _:
                ic('blocked', url)


class WebEnginePage(qt.QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)

        settings = self.settings()
        settings.setAttribute(qt.QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, False)
        settings.setAttribute(qt.QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(qt.QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(qt.QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
        settings.setAttribute(qt.QWebEngineSettings.WebAttribute.NavigateOnDropEnabled, False)

        self._interceptor = interceptor = Interceptor(self)
        self.setUrlRequestInterceptor(interceptor)

    # def acceptNavigationRequest(self, url, type, isMainFrame):
    #     if not url.url().startswith('data:'):
    #         ic(url)
    #     # to handle html, return False, and use setHtml
    #     return True


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        doc = self.server._doc

        path = self.path.lstrip('/')
        if '?' in path:
            path = path.split('?')[0]
        if '#' in path:
            path = path.split('#')[0]

        if path not in doc:
            if not path.endswith('.html') and (path + '.html') in doc:
                path = path + '.html'
            elif (path.rstrip('/') + '/index.html') in doc:
                path = path.rstrip('/') + '/index.html'
            else:
                self.send_content(f'Path {path} not found in {doc.path}', status=HTTPStatus.NOT_FOUND)
                return

        self.send_response(HTTPStatus.OK)

        mime = mime_db.mimeTypeForFile(path, qt.QMimeDatabase.MatchMode.MatchExtension)
        assert mime.isValid(), path
        self.send_header('Content-Type', mime.name())

        content = doc[path]
        self.send_header('Content-Length', len(content))

        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'max-age=604800')  # make js/css cached by the client
        self.end_headers()

        self.wfile.write(content)

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
    def __init__(self, server, parent=None):
        super().__init__(parent)
        self._server = server

    def run(self):
        self._server.serve_forever()


class Widget(qt.QWidget):
    _title_changed = qt.Signal(str)

    def __init__(self, name, **kwargs):
        super().__init__()

        self._name = name
        self._index_page = kwargs.pop('index', 'index.html').lstrip('/')
        self._kwargs = kwargs
        self._initialized = False

    def _cleanup(self):
        if self._initialized:
            self._server.shutdown()

    def _init(self):
        if self._initialized:
            return

        self._doc = format.create_instance(self._name, **self._kwargs)

        self._server = server = ThreadingHTTPServer(('127.0.0.1', 0), RequestHandler)
        server._doc = self._doc
        self._thread = thread = Thread(server, self)
        thread.start()

        self._prefix = f'http://127.0.0.1:{self._server.server_port}/'

        self._setup_ui()

        self._initialized = True

    def _setup_ui(self):
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = splitter = qt.QSplitter()
        layout.addWidget(splitter)

        self._page = page = WebEnginePage(self)
        self._webengine = webengine = WebEngineView(page)
        splitter.addWidget(webengine)

        doc = self._doc
        if doc.has_index():
            self._index = index = IndexWidget(doc)
            index.sizePolicy().setHorizontalPolicy(qt.QSizePolicy.Policy.Fixed)
            splitter.addWidget(index)
            index._item_clicked.connect(self._on_index_clicked)
        else:
            self._index = None

        page.titleChanged.connect(self._title_changed)

        webengine.load(qt.QUrl(self._prefix + self._index_page))

    def _on_index_clicked(self, location):
        if '#' in location:
            href, hash = location.split('#', 1)
            url = qt.QUrl(self._prefix + href.lstrip('/'))
            if hash:
                url.setFragment(hash)
        else:
            url = qt.QUrl(self._prefix + location.lstrip('/'))
        ic(url)
        self._page.setUrl(url)
