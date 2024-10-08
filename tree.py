import yaml
from path import Path

from . import ICONS_DIR, Qt, qt
from .format import get_format

SELECTED_BG = '#2468AB'
GROUP_ICON = qt.QIcon(ICONS_DIR / 'group.png')

icons_cache = {}


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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setItemDelegate(Delegate(self))
        self.header().setSectionResizeMode(0, qt.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setStretchLastSection(False)
        self.setSizeAdjustPolicy(qt.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setMouseTracking(True)
        self.setStyleSheet(
            """
            QTreeWidget::item { border: 0; padding: 2px 10px; }
            QTreeWidget::item:hover { border: 0; background: '%s' }
            QTreeView::branch {  border-image: url(none.png) }
        """
            % SELECTED_BG
        )

        self._id = 0  # next_id counter
        self._start_item = None  # item to open on application start
        with (Path(__file__).parent / 'docs' / 'docs.yaml').open() as f:
            self._load(yaml.load(f, Loader=yaml.CLoader), self)
        self.expandAll()

    def _next_id(self):
        self._id += 1
        return self._id

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

    def _load(self, items, parent):
        for name, params in items.items():
            if params is None:
                params = {}

            if name[0] == '.':
                item = self._add_group(name[1:], parent)
                self._load(params, item)
            else:
                format = get_format(name, params)
                item = self._add_item(name, params, format, parent)
                children = params.pop('children', None)
                if children:
                    self._load(children, item)

    def _add_group(self, label, parent):
        item = qt.QTreeWidgetItem(parent)
        item.setText(0, label)
        item.setFlags(Qt.ItemIsEnabled)
        item.setForeground(0, qt.QBrush(Qt.lightGray))
        item.setIcon(0, GROUP_ICON)
        return item

    def _add_item(self, name, params, format, parent):
        global icons_cache
        item = qt.QTreeWidgetItem(parent)
        item.setText(0, name)
        if format not in icons_cache:
            icons_cache[format] = qt.QIcon(ICONS_DIR / f'{format}.png')
        item.setIcon(0, icons_cache[format])
        item.setData(0, Qt.UserRole, (self._next_id(), name, params, format))
        if name == 'python':
            self._start_item = item
        return item
