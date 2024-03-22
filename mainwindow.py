import os

from . import Qt, qt, settings, utils
from .viewer import Widget as Viewer


class TabWidget(qt.QTabWidget):
    _title_changed = qt.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._tab_titles = {}

        self.currentChanged.connect(self._on_current_changed)

    def addDoc(self, name, title=None, index_page=None, **kwargs):
        viewer = Viewer(name, index_page, kwargs)
        self.addTab(viewer, title or os.path.splitext(name)[0])

        viewer._title_changed.connect(self._on_title_changed)

    def _on_current_changed(self, index):
        self.currentWidget()._init()
        if index in self._tab_titles:
            self._title_changed.emit(self._tab_titles[index])

    def _on_title_changed(self, title):
        self._tab_titles[self.currentIndex()] = title
        self._title_changed.emit(title)


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self._restored = False

        self._setup_ui()

        utils.shortcuts(
            self,
            {
                Qt.Key_Left: self._back,
                Qt.Key_Right: self._forward,
            },
        )

    def _setup_ui(self):
        self._tabs = tabs = TabWidget()
        self.setCentralWidget(tabs)

        tabs._title_changed.connect(self._update_title)

        tabs.addDoc('matplotlib')
        tabs.addDoc('numpy')
        tabs.addDoc('numba', prefix='docs/html')
        tabs.addDoc('scipy')
        tabs.addDoc('polars', prefix='py-polars/html')
        tabs.addDoc('python-3.12.2-docs-html.zip', title='python')
        tabs.addDoc('duckdb.zip', title='duckdb', index_page='docs/index.html')
        tabs.addDoc('qt-6.6.2.zip', title='qt', index_page='qtdoc/index.html')
        tabs.addDoc('streamlit.sqlite', prefix='https://docs.streamlit.io/')

    def keyPressEvent(self, event):
        # uppercase letter is determined by shift key, the code is the same with the lowercase letter
        if Qt.Key_A <= event.key() <= Qt.Key_Z and event.modifiers() == Qt.NoModifier:
            self._search_index(event.text())
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        settings['window.geometry'] = self.saveGeometry()
        # settings['window.dock'] = self._dock_manager.saveState()

        tabs = self._tabs
        for i in range(tabs.count()):
            tabs.widget(i)._cleanup()

    def showEvent(self, event):
        super().showEvent(event)
        if not self._restored:
            try:
                if geometry := settings.get('window.geometry'):
                    self.restoreGeometry(geometry)
                # if state := settings.get('window.dock'):
                #     self._dock_manager.restoreState(state)
            except TypeError:
                pass
            self._restored = True

    def changeEvent(self, event):
        if event.type() == qt.QEvent.Type.ActivationChange and self.isActiveWindow():
            qt.setLastHwnd(self)
            # self._fixDockGeometry()

    def _back(self):
        self._tabs.currentWidget()._page.triggerAction(qt.QWebEnginePage.WebAction.Back)

    def _forward(self):
        self._tabs.currentWidget()._page.triggerAction(qt.QWebEnginePage.WebAction.Forward)

    def _search_index(self, text):
        if index := self._tabs.currentWidget()._index:
            edit = index._edit
            edit.setFocus(Qt.OtherFocusReason)
            edit.setText(text)

    def _update_title(self, title):
        tabs = self._tabs
        tab_label = tabs.tabText(tabs.currentIndex())
        if title:
            text = f'{tab_label} | {title}'
        else:
            text = tab_label
        self.setWindowTitle(text)
