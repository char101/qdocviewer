from . import ICONS_DIR, Qt, format, qt
from .viewer import Widget as Viewer

SELECTED_BG = '#2468AB'
DIRECTORY_ICON = qt.QIcon(ICONS_DIR / 'directory.png')
ZIPPED_ICON = qt.QIcon(ICONS_DIR / 'zipped.png')
INTERNET_ICON = qt.QIcon(ICONS_DIR / 'internet.png')
GROUP_ICON = qt.QIcon(ICONS_DIR / 'group.png')


class Delegate(qt.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index == self.parent().currentIndex():
            painter.save()
            painter.setPen(qt.QPen(Qt.NoPen))
            painter.setBrush(qt.QBrush(qt.QColor(SELECTED_BG)))
            painter.drawRect(option.rect)
            painter.restore()

        super().paint(painter, option, index)


class TreeWidget(qt.QTreeWidget):
    _letter_pressed = qt.Signal(str)

    def mouseMoveEvent(self, event):
        if self.indexAt(event.pos()).isValid() and self.itemAt(event.pos()).data(0, Qt.UserRole) is not None:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def keyPressEvent(self, event):
        key = event.key()
        if Qt.Key_A <= key <= Qt.Key_Z:
            self._letter_pressed.emit(event.text())
            return
        super().keyPressEvent(event)

    # def sizeHint(self):
    #     s = super().sizeHint()
    #     return qt.QSize(s.width() + 10, s.height())


class Widget(qt.QWidget):
    _title_changed = qt.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tab_titles = {}
        self._next_index = 0

        self._setup_ui()

    def _setup_ui(self):
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tree = tree = TreeWidget(self)
        tree.setFocusPolicy(Qt.NoFocus)
        tree.setUniformRowHeights(True)
        tree.setHeaderHidden(True)
        tree.setRootIsDecorated(False)
        tree.setItemDelegate(Delegate(tree))
        tree.header().setSectionResizeMode(0, qt.QHeaderView.ResizeMode.ResizeToContents)
        tree.header().setStretchLastSection(False)
        tree.setSizeAdjustPolicy(qt.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        tree.setMouseTracking(True)
        tree.setStyleSheet('QTreeWidget::item { border: 0; padding: 2px 10px; } QTreeWidget::item:hover { border: 0; background: ' + SELECTED_BG + '; }')
        layout.addWidget(tree)

        self._stack = stack = qt.QStackedWidget()
        layout.addWidget(stack, 1)

        @stack.currentChanged
        def _(index):
            self._stack.widget(index)._init()
            if index in self._tab_titles:
                self._title_changed.emit(self._tab_titles[index])
        @tree.itemClicked
        def _(item):
            index = item.data(0, Qt.UserRole)
            if index is not None:
                self._stack.setCurrentIndex(index)
        @tree._letter_pressed
        def _(text):
            if index := self._stack.currentWidget()._index:
                index._search(text)

    def _add_group(self, label, parent=None):
        if parent is None:
            parent = self._tree
        item = qt.QTreeWidgetItem(parent)
        item.setText(0, label)
        item.setFlags(Qt.ItemIsEnabled)
        item.setForeground(0, qt.QBrush(Qt.lightGray))
        item.setIcon(0, GROUP_ICON)
        return item

    def _add_doc(self, name, path, start=None, params={}, parent=None):
        if parent is None:
            parent = self._tree
        index = self._next_index
        self._next_index += 1

        item = qt.QTreeWidgetItem(parent)
        item.setText(0, name)
        item.setData(0, Qt.UserRole, index)
        match format.get_type(path, params):
            case format.DirectoryDoc:
                item.setIcon(0, DIRECTORY_ICON)
            case format.ZippedDoc:
                item.setIcon(0, ZIPPED_ICON)
            case format.CachedDoc:
                item.setIcon(0, INTERNET_ICON)

        viewer = Viewer(path, start=start, doc_options=params)
        self._stack.addWidget(viewer)

        @viewer._title_changed
        def _(title, _index=index):
            self._tab_titles[_index] = title
            if _index == self._stack.currentIndex():
                self._title_changed.emit(title)

        if index == 0:
            self._tree.setCurrentItem(item)

        return item

    def __iter__(self):
        stack = self._stack
        for i in range(stack.count()):
            yield stack.widget(i)
