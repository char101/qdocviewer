import os

import yaml
from path import Path

from . import Qt, qt, settings, utils
from .treetab import Widget as TreeTab


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self._restored = False

        self._setup_ui()
        self._load_docs()
        self._tabs._tree.expandAll()

        utils.shortcuts(
            self,
            {
                Qt.Key_Left: self._back,
                Qt.Key_Right: self._forward,
            },
        )

    def _load_docs(self):
        tree = self._tabs

        def load(items, parent=None):
            for name in items.keys() if parent is None else sorted(items.keys()):
                params = items[name]
                if params is None:
                    params = {}

                if name[0] == '.':
                    load(params, tree._add_group(name[1:], parent))
                else:
                    children = params.pop('children', None)
                    path = params.pop('path', name)
                    start = params.pop('start', None)

                    item = tree._add_doc(name, path, start, params, parent=parent)

                    if children:
                        load(children, item)

        with Path(__file__).parent.joinpath('docs.yaml').open() as f:
            load(yaml.load(f, Loader=yaml.CLoader))

    def _setup_ui(self):
        self._tabs = tabs = TreeTab()
        self.setCentralWidget(tabs)

        tabs._title_changed.connect(self._update_title)

    def keyPressEvent(self, event):
        # uppercase letter is determined by shift key, the code is the same with the lowercase letter
        if Qt.Key_A <= event.key() <= Qt.Key_Z and event.modifiers() == Qt.NoModifier:
            self._search_index(event.text())
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        settings['window.geometry'] = self.saveGeometry()
        # settings['window.dock'] = self._dock_manager.saveState()

        for w in self._tabs:
            w._cleanup()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._restored:
            try:
                if geometry := settings.get('window.geometry'):
                    self.restoreGeometry(geometry)
            except TypeError:
                pass
            self._restored = True

    def changeEvent(self, event):
        if event.type() == qt.QEvent.Type.ActivationChange and self.isActiveWindow():
            qt.setLastHwnd(self)

    def _back(self):
        self._tabs._stack.currentWidget()._page.triggerAction(qt.QWebEnginePage.WebAction.Back)

    def _forward(self):
        self._tabs._stack.currentWidget()._page.triggerAction(qt.QWebEnginePage.WebAction.Forward)

    def _search_index(self, text):
        if index := self._tabs._stack.currentWidget()._index:
            edit = index._edit
            edit.setFocus(Qt.OtherFocusReason)
            edit.setText(text)

    def _update_title(self, title):
        tabs = self._tabs
        if item := tabs._tree.currentItem():
            tab_label = item.text(0)
            if title:
                text = f'{tab_label} | {title}'
            else:
                text = tab_label
            self.setWindowTitle(text)
