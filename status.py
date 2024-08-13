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

        self._counter = w = qt.QLabel(self)
        self.addWidget(w)

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
        path = url.path()[1:]  # remove leading /
        text = path
        if item := self.parent()._stack.currentWidget()._doc[path]:
            text += f' [{datetime.fromtimestamp(item.updated).strftime('%Y-%m-%d')}]'
        self._doc_url.setText(text)

    def _update_counter(self):
        if viewer := self.parent()._stack.currentWidget():
            doc = viewer._doc
            if hasattr(doc, 'counter'):
                counter = doc.counter
                texts = []
                for k, color in {'fetch': '#63C885', 'cache': '#6AB3E7', 'block': '#FF8C8C', 'refresh': '#BDA434'}.items():
                    if counter[k]:
                        texts.append(f'<span style="color:{color}">{k.upper()}</span> {counter[k]}')
                self._counter.setText(' '.join(texts))
