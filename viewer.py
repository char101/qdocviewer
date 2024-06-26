import logging
from urllib.parse import urljoin

from . import USERSCRIPTS_DIR, format, qt, term
from .index import Widget as IndexWidget
from .server import HttpServer

logger = logging.getLogger(__name__)


class Interceptor(qt.QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__(parent)
        self._doc = parent.parent()._doc

    def interceptRequest(self, info):
        url = info.requestUrl()

        def block():
            logger.warn('%s %s', term.red('BLOCK'), url.url())
            info.block(True)

        method = info.requestMethod()
        if method != b'GET':
            print(term.red('BLOCKED'), term.yellow(str(method)), url)
            info.block(True)

        doc = self._doc
        server_prefix = self.parent().parent()._prefix
        match url.scheme():
            case 'https':
                if isinstance(doc, format.CachedDoc) and url.url().startswith(doc.prefix):
                    new_url = urljoin(server_prefix, url.path())
                    # ic('redirect', url.url(), new_url)
                    info.redirect(qt.QUrl(new_url))
                elif doc.is_whitelisted(url):
                    new_url = qt.QUrl(server_prefix + url.url())
                    # ic('redirect', url.url(), new_url)
                    info.redirect(new_url)
                else:
                    block()
            case 'http':
                if url.host() != '127.0.0.1':
                    if isinstance(doc, format.CachedDoc) and url.url().startswith(doc.prefix):
                        new_url = urljoin(server_prefix, url.path())
                        # ic('redirect', url.url(), new_url)
                        info.redirect(qt.QUrl(new_url))
                    elif doc.is_whitelisted(url):
                        new_url = qt.QUrl(server_prefix + url.url())
                        # ic('redirect', url.url(), new_url)
                        info.redirect(new_url)
                    else:
                        block()
            case 'file':
                block()
            case 'data':
                pass
            case _:
                block()


class WebEnginePage(qt.QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)

        settings = self.settings()
        wa = qt.QWebEngineSettings.WebAttribute
        settings.setAttribute(wa.JavascriptCanOpenWindows, False)
        settings.setAttribute(wa.WebGLEnabled, False)
        settings.setAttribute(wa.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(wa.AutoLoadIconsForPage, False)
        settings.setAttribute(wa.NavigateOnDropEnabled, False)

        self._interceptor = interceptor = Interceptor(self)
        self.setUrlRequestInterceptor(interceptor)


class Widget(qt.QWidget):
    _title_changed = qt.Signal(str)

    def __init__(self, name, path, start=None, doc_options={}):
        super().__init__()

        self._name = name
        self._path = path
        self._start = start
        self._doc_options = doc_options
        self._initialized = False

    def _cleanup(self):
        if self._initialized:
            self._server.stop()
            self._doc.stop()

    def _init(self):
        if self._initialized:
            return

        self._doc = format.create_instance(self._name, self._path, self._doc_options)

        self._server = HttpServer(self._doc)
        self._server.start()
        self._prefix = self._server.prefix

        self._setup_ui()

        self._initialized = True

        url = qt.QUrl(self._prefix)
        if self._start:
            url.setPath('/' + self._start.lstrip('/'))
        self._webengine.load(url)

    def _setup_ui(self):
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = splitter = qt.QSplitter()
        layout.addWidget(splitter)

        self._page = page = WebEnginePage(self)
        self._webengine = webengine = qt.QWebEngineView(page)
        splitter.addWidget(webengine)

        doc = self._doc
        if (res := doc.get_index()) is not None:
            self._index = index = IndexWidget(res)
            index.sizePolicy().setHorizontalPolicy(qt.QSizePolicy.Policy.Fixed)
            splitter.addWidget(index)
            index._item_clicked.connect(self._on_index_clicked)
        else:
            self._index = None

        userscript_file = USERSCRIPTS_DIR / f'{self._name}.js'
        if userscript_file.exists():
            self._set_userscript(userscript_file)

        page.titleChanged.connect(self._title_changed)

    def _on_index_clicked(self, location):
        if '#' in location:
            href, hash = location.split('#', 1)
            url = qt.QUrl(self._prefix + href.lstrip('/'))
            if hash:
                url.setFragment(hash)
        else:
            url = qt.QUrl(self._prefix + location.lstrip('/'))
        self._page.setUrl(url)

    def _set_userscript(self, path):
        scripts = self._page.scripts()

        scripts.clear()  # cannot edit existing script

        if path.exists() and path.size > 0:
            script = qt.QWebEngineScript()
            script.setInjectionPoint(qt.QWebEngineScript.InjectionPoint.DocumentReady)
            script.setSourceCode('(function() {' + path.read_text() + '})()')
            scripts.insert(script)

    def _remove_userscript(self):
        self._page.scripts().clear()
