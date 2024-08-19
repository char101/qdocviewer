import logging
from urllib.parse import urljoin

from recordclass import dataobject

from . import DOCS_DIR, Qt, qt, term
from .index import Widget as IndexWidget
from .server import HttpServer

logger = logging.getLogger(__name__)


class UserScript(dataobject):
    name: str
    file: str
    prefix: str = ''
    suffix: str = ''
    time: int = None
    script: qt.QWebEngineScript = None


class Interceptor(qt.QWebEngineUrlRequestInterceptor):
    def __init__(self, parent):
        super().__init__(parent)
        self._doc = parent.parent()._doc

    def interceptRequest(self, info):
        url = info.requestUrl()

        def block():
            logger.warn('%s %s', term.red('BLOCK'), url.url())
            info.block(True)
            self._doc.counter['block'] += 1

        method = info.requestMethod()
        if method != b'GET':
            print(term.red('BLOCKED'), term.yellow(str(method)), url)
            info.block(True)
            self._doc.counter['block'] += 1

        doc = self._doc
        server_prefix = self.parent().parent()._prefix
        match url.scheme():
            case 'https':
                if doc.format == 'mirror' and url.url().startswith(doc.prefix):
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
                    if doc.format == 'mirror' and url.url().startswith(doc.prefix):
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
        self.setBackgroundColor(qt.QColor('#333333'))

        settings = self.settings()
        wa = qt.QWebEngineSettings.WebAttribute
        settings.setAttribute(wa.JavascriptCanOpenWindows, False)
        settings.setAttribute(wa.WebGLEnabled, False)
        settings.setAttribute(wa.Accelerated2dCanvasEnabled, False)
        settings.setAttribute(wa.AutoLoadIconsForPage, False)
        settings.setAttribute(wa.NavigateOnDropEnabled, False)

        settings.setFontFamily(qt.QWebEngineSettings.FontFamily.StandardFont, 'Segoe UI')
        settings.setFontFamily(qt.QWebEngineSettings.FontFamily.SansSerifFont, 'Segoe UI')
        settings.setFontFamily(qt.QWebEngineSettings.FontFamily.SerifFont, 'Noto Serif')
        settings.setFontFamily(qt.QWebEngineSettings.FontFamily.FixedFont, 'Cascadia Mono')

        self._interceptor = interceptor = Interceptor(self)
        self.setUrlRequestInterceptor(interceptor)


class ViewerWidget(qt.QWidget):
    def __init__(self, doc):
        super().__init__()

        self._doc = doc
        self._server = HttpServer(self._doc)
        self._server.start()
        self._prefix = self._server.prefix
        self._userscripts = (
            UserScript('userscript', DOCS_DIR / doc.name / f'{doc.name}.js'),
            UserScript('userstyle', DOCS_DIR / doc.name / f'{doc.name}.css', prefix='const css = new CSSStyleSheet(); css.replaceSync(`', suffix='`); document.adoptedStyleSheets.push(css);'),
        )
        self._userstyle_file = DOCS_DIR / self._doc.name / f'{self._doc.name}.css'
        self._userscript_time = None
        self._userstyle_time = None

        self._setup_ui()

        url = qt.QUrl(self._prefix)
        if start := self._doc.start:
            url.setPath('/' + start.lstrip('/'))
        self._webengine.load(url)

    def _cleanup(self):
        self._server.stop()
        self._doc.stop()

    def _setup_ui(self):
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = splitter = qt.QSplitter(self)
        layout.addWidget(splitter)

        self._inspector_splitter = inspector_splitter = qt.QSplitter(Qt.Vertical, self)
        splitter.addWidget(inspector_splitter)

        self._page = page = WebEnginePage(self)
        page.loadStarted.connect(self._doc.reset_counter)
        page.navigationRequested.connect(lambda _: self._load_userscript())
        self._webengine = webengine = qt.QWebEngineView(page)
        inspector_splitter.addWidget(webengine)

        # placeholder for inspector
        self._inspector_page = None
        self._inspector_view = None

        doc = self._doc
        if (res := doc.get_index()) is not None:
            self._index = index = IndexWidget(res)
            index.sizePolicy().setHorizontalPolicy(qt.QSizePolicy.Policy.Fixed)
            splitter.addWidget(index)
            index._item_clicked.connect(self._on_index_clicked)
        else:
            self._index = None

        self._load_userscript()

    def _on_index_clicked(self, location):
        if '#' in location:
            href, hash = location.split('#', 1)
            url = qt.QUrl(self._prefix + href.lstrip('/'))
            if hash:
                url.setFragment(hash)
        else:
            url = qt.QUrl(self._prefix + location.lstrip('/'))
        self._page.setUrl(url)

    def _load_userscript(self):
        scripts = self._page.scripts()
        for us in self._userscripts:
            file = us.file
            if file.exists() and file.size > 0:
                if us.time is None or us.time < file.mtime:
                    script = qt.QWebEngineScript()
                    script.setName(us.name)
                    script.setInjectionPoint(qt.QWebEngineScript.InjectionPoint.DocumentReady)
                    script.setSourceCode('(function() {' + us.prefix + file.read_text() + us.suffix + '})();')

                    if us.script:
                        scripts.remove(us.script)
                    scripts.insert(script)
                    us.time = file.mtime
                    us.script = script
            else:
                # file is deleted
                if us.script:
                    scripts.remove(us.script)
                    us.time = None
                    us.script = None

    def _toggle_inspector(self):
        if self._inspector_page is None:
            self._inspector_page = page = qt.QWebEnginePage(self)
            page.setBackgroundColor(qt.QColor('#282828'))
            page.setInspectedPage(self._page)
            page.windowCloseRequested.connect(self._toggle_inspector)
            self._inspector_view = view = qt.QWebEngineView(page, self)
            self._inspector_splitter.addWidget(view)
            size = self._inspector_splitter.sizes()
            if size[1] == 0:
                h = size[0] // 3
                self._inspector_splitter.setSizes([size[0] - h, h])
        else:
            # deleting the widget will automatically remote it from the splitter
            self._inspector_page.deleteLater()
            self._inspector_view.deleteLater()
            self._inspector_page = None
            self._inspector_view = None
