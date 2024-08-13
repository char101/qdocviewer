from . import Qt, format, qt
from .viewer import ViewerWidget


class StackWidget(qt.QStackedWidget):
    _title_changed = qt.Signal(str)
    _url_changed = qt.Signal(qt.QUrl)
    _doc_changed = qt.Signal(object)
    _load_finished = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._viewers = {}
        self._page_titles = {}

    def _open(self, data):
        id, name, params, fmt = data

        if not fmt:
            return

        if id not in self._viewers:
            doc = format.create_instance(name, params, fmt)
            viewer = ViewerWidget(doc)
            index = self.count()
            self.addWidget(viewer)
            self._viewers[id] = index

            @viewer._page.titleChanged
            def _(title):
                self._page_titles[index] = title
                if index == self.currentIndex():
                    self._title_changed.emit(title)
            viewer._page.urlChanged.connect(self._url_changed)
            viewer._page.loadFinished.connect(self._load_finished)
        else:
            index = self._viewers[id]

        self.setCurrentIndex(index)
        self._doc_changed.emit(self.currentWidget()._doc)
        self.currentWidget().setFocus(Qt.MouseFocusReason)
