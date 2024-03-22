from rapidfuzz.fuzz import WRatio as scorer
from rapidfuzz.process import extract as search

from . import Qt, qt

# from rapidfuzz.utils import default_process


class WorkerSignals(qt.QObject):
    _finished = qt.Signal()
    _error = qt.Signal(str)
    _result = qt.Signal(list)


class SearchTask(qt.QRunnable):
    _search_finished = qt.Signal(list)

    def __init__(self, search, symbols):
        super().__init__()
        self._search = search
        self._symbols = symbols
        self._signals = WorkerSignals()

    def run(self):
        try:
            if self._search is None or self._search == '':
                result = [None]
            else:
                result = search(self._search, self._symbols, scorer=scorer, limit=20)
            self._signals._result.emit(result)
        except Exception as err:
            self._signals._error.emit(str(err))
        finally:
            self._signals._finished.emit()


class Model(qt.QAbstractListModel):
    def __init__(self, symbols, locations):
        super().__init__()
        self._symbols = symbols
        self._locations = locations
        self._items = self._symbols
        self._item_locations = locations
        self._thread_pool = qt.QThreadPool()
        self._thread_pool.setMaxThreadCount(1)

    def rowCount(self, index):
        return len(self._items)

    def multiData(self, index, roleDataSpan):
        for roleData in roleDataSpan:
            if roleData.role() == Qt.DisplayRole:
                roleData.setData(self._items[index.row()])

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._items[index.row()]

    def _filter(self, text):
        pool = self._thread_pool
        pool.clear()

        task = SearchTask(text.strip(), self._symbols)
        task.setAutoDelete(True)
        task._signals._result.connect(self._on_search_result)
        task._signals._error.connect(lambda err: qt.showWarning(err))
        pool.start(task)

    def _on_search_result(self, result):
        self.beginResetModel()
        if result[0] is None:
            self._items = self._symbols
            self._item_locations = self._locations
        else:
            self._items = tuple(res[0] for res in result)
            locations = self._locations
            self._item_locations = tuple(locations[res[2]] for res in result)
        self.endResetModel()


class List(qt.QListView):
    _item_clicked = qt.Signal(str)
    _key_up = qt.Signal()
    _letter_pressed = qt.Signal(str)

    def __init__(self, data):
        super().__init__()

        self.setMouseTracking(True)
        self.setStyleSheet('QListView::item:hover { color: yellow }')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTextElideMode(Qt.ElideNone)
        # this half the time required to load large items
        self.setUniformItemSizes(True)
        self.setLayoutMode(qt.QListView.LayoutMode.Batched)

        symbols, locations = data
        self._model = model = Model(symbols, locations)
        self.setModel(model)

        self.clicked.connect(self._on_clicked)

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
                self._on_clicked(index)
                return
        elif Qt.Key_A <= key <= Qt.Key_Z:
            self._letter_pressed.emit(event.text())
            return
        super().keyPressEvent(event)

    def _filter(self, text):
        self._model._filter(text)

    def _on_clicked(self, index):
        if index.isValid():
            location = self._model._item_locations[index.row()]
            self._item_clicked.emit(location)


class LineEdit(qt.QLineEdit):
    _key_down = qt.Signal()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if event.reason() != Qt.OtherFocusReason:
            qt.QTimer.singleShot(0, self.selectAll)

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key_Down:
                self._key_down.emit()
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

        self._list = lst = List(data)
        layout.addWidget(lst)

        self._timer = timer = qt.QTimer()
        timer.setSingleShot(True)
        timer.setInterval(100)

        edit.textChanged.connect(self._on_text_changed)
        edit._key_down.connect(self._focus_list)
        timer.timeout.connect(self._on_timer)
        lst._item_clicked.connect(self._item_clicked)
        lst._key_up.connect(self._focus_edit)
        lst._letter_pressed.connect(self._on_list_letter_pressed)

    def sizeHint(self):
        return qt.QSize(120, 100)

    def _on_text_changed(self, text):
        self._search_text = text
        self._timer.stop()
        self._timer.start()

    def _on_timer(self):
        self._list._filter(self._search_text)

    def _focus_list(self):
        self._list.setFocus(Qt.TabFocusReason)

    def _focus_edit(self):
        self._edit.setFocus(Qt.TabFocusReason)

    def _on_list_letter_pressed(self, text):
        edit = self._edit
        edit.setFocus(Qt.OtherFocusReason)
        edit.setText(text)
