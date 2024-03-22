from . import format, qt
from .index import Widget as IndexWidget
from .server import HttpServer


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

    def __init__(self, name, index_page=None, doc_options={}):
        super().__init__()

        self._name = name
        self._index_page = index_page.lstrip('/') if index_page else 'index.html'
        self._doc_options = doc_options
        self._initialized = False

    def _cleanup(self):
        if self._initialized:
            self._server.stop()

    def _init(self):
        if self._initialized:
            return

        self._doc = format.create_instance(self._name, **self._doc_options)

        self._server = HttpServer(self._doc)
        self._server.start()
        self._prefix = self._server.prefix

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
        if res := doc.get_index():
            self._index = index = IndexWidget(res)
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
        self._page.setUrl(url)
