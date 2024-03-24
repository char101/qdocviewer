from . import qt


class TreeTab(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tree = tree = qt.QTreeWidget()
        layout.addWidget(tree)
        self._stack = stack = qt.QStackedWidget()
        layout.addWidget(stack)

    def addTab(self, widget, label):
        pass
