from datetime import datetime

from . import qt


class StatusBar(qt.QStatusBar):
    _search_changed = qt.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._doc_path = w = qt.QLabel(self)
        self.addWidget(w)

        self._doc_url = w = qt.QLabel(self)
        self.addWidget(w)

        # self._doc_time = w = qt.QLabel(self)
        # self.addWidget(w)

        self._search = w = qt.QLineEdit(self)
        w.setSizePolicy(qt.QSizePolicy.Policy.Minimum, qt.QSizePolicy.Policy.Preferred)
        self.addPermanentWidget(w)
        @w.textEdited
        def _(text):
            text = text.strip()
            if len(text) >= 3:
                self._search_changed.emit(text)

    def _set_doc(self, doc):
        if doc.format == 'mirror':
            if baseline := doc.get_prop('baseline'):
                text = f'{doc.prefix} [{datetime.fromtimestamp(baseline).strftime('%Y-%m-%d')}]'
            else:
                text = doc.prefix
        else:
            text = doc.path
        self._doc_path.setText(text)

    def _set_url(self, url):
        path = url.path()[1:]

        self._doc_url.setText(path)

        # item = self.parent()._stack.currentWidget()._doc[path]
        # if item:
        #     self._doc_time.setText(datetime.fromtimestamp(item.updated).isoformat(' '))
