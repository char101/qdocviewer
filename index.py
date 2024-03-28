import re

import polars as pl

from . import Qt, qt

MAX_RESULT = 50
ws_re = re.compile(r'\s+')


class Model(qt.QAbstractListModel):
    def __init__(self, df):
        super().__init__()

        df.sort('symbol')
        self._df = df

        self._items = self._df

    def rowCount(self, index):
        return len(self._items)

    def multiData(self, index, roleDataSpan):
        for roleData in roleDataSpan:
            if roleData.role() == Qt.DisplayRole:
                roleData.setData(self._items[index.row(), 'symbol'])

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._items[index.row(), 'symbol']

    def _filter(self, text):
        if text is None or text == '' or len(text) < 3:
            result = self._df
        else:
            df = self._df
            words = ws_re.split(text)

            word = words.pop(0).lower()
            result = df.filter(pl.col('symbol').str.to_lowercase().str.starts_with(word))
            if len(result) < MAX_RESULT:
                result = result.vstack(df.filter(pl.col('symbol').str.to_lowercase().str.contains(word)))

            # subsequent words are used to filter the result
            for word in words:
                result = result.filter(pl.col('symbol').str.to_lowercase().str.contains(word.lower()))

        if result is not self._items:
            self.beginResetModel()
            self._items = result
            self.endResetModel()


class List(qt.QListView):
    _item_clicked = qt.Signal(str)
    _key_up = qt.Signal()
    _letter_pressed = qt.Signal(str)

    def __init__(self, df):
        super().__init__()

        self.setMouseTracking(True)
        self.setStyleSheet('QListView::item:hover { background-color: #887003 }')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextElideMode(Qt.ElideNone)
        # this half the time required to load large items
        self.setUniformItemSizes(True)
        self.setLayoutMode(qt.QListView.LayoutMode.Batched)

        self._model = model = Model(df)
        self.setModel(model)

        self.clicked.connect(self._open_location)

    def mouseMoveEvent(self, event):
        if self.indexAt(event.pos()).isValid():
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            index = self.currentIndex()
            if index.isValid() and index.row() == 0:
                self._key_up.emit()
                return
        elif key == Qt.Key_Return:
            index = self.currentIndex()
            if index.isValid():
                self._open_location(index)
                return
        elif Qt.Key_A <= key <= Qt.Key_Z:
            self._letter_pressed.emit(event.text())
            return
        super().keyPressEvent(event)

    def _filter(self, text):
        self._model._filter(text)

    def _open_location(self, index):
        if index.isValid():
            location = self._model._items[index.row(), 'location']
            self._item_clicked.emit(location)


class LineEdit(qt.QLineEdit):
    _key_down = qt.Signal()
    _key_enter = qt.Signal()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if event.reason() != Qt.OtherFocusReason:
            qt.QTimer.singleShot(0, self.selectAll)

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key_Down:
                self._key_down.emit()
            case Qt.Key_Return | Qt.Key_Enter:
                self._key_enter.emit()
            case Qt.Key_Escape:
                self.setText('')
            case _:
                super().keyPressEvent(event)


class Widget(qt.QWidget):
    _item_clicked = qt.Signal(str)

    def __init__(self, data):
        super().__init__()

        self._search_text = None

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._edit = edit = LineEdit()
        layout.addWidget(edit)
        @edit.textChanged
        def _(text):
            self._search_text = text
            self._timer.stop()
            self._timer.start()

        edit._key_down.connect(lambda: qt.QTimer.singleShot(0, self._focus_list))
        edit._key_enter.connect(self._select_first_result)

        self._list = lst = List(data)
        layout.addWidget(lst)
        lst._item_clicked.connect(self._item_clicked)
        lst._key_up.connect(self._focus_edit)
        lst._letter_pressed.connect(self._search)

        self._timer = timer = qt.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(100)
        timer.timeout.connect(lambda: self._list._filter(self._search_text))

    def sizeHint(self):
        return qt.QSize(150, 100)

    def _focus_edit(self):
        self._edit.setFocus(Qt.TabFocusReason)

    def _focus_list(self):
        ls = self._list
        ls.setFocus(Qt.TabFocusReason)
        ls.setCurrentIndex(ls._model.index(0, 0, qt.QModelIndex()))

    def _select_first_result(self):
        model = self._list._model
        if len(model._items):
            self._item_clicked.emit(model._items[0, 'location'])

    def _search(self, text):
        edit = self._edit
        edit.setFocus(Qt.OtherFocusReason)
        edit.setText(text)
