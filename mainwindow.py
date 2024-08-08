from path import Path

from . import DOCS_DIR, Qt, qt, settings, utils
from .stack import StackWidget
from .status import StatusBar
from .tree import TreeWidget


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self._restored = False

        self._setup_ui()

        utils.shortcuts(self, {
            Qt.Key_Left: lambda: self._trigger_action('Back'),
            Qt.Key_Right: lambda: self._trigger_action('Forward'),
            Qt.Key_F5: lambda: self._trigger_action('Reload'),
            Qt.SHIFT | Qt.Key_F5: self._set_baseline,
            Qt.CTRL | Qt.Key_F: self._search,
            Qt.Key_F3: self._search_next,
            Qt.SHIFT | Qt.Key_F3: self._search_prev,
            Qt.Key_Escape: self._search_clear,
        },)

        userscripts_dir = DOCS_DIR / '_userscripts'
        self._userscripts = {file.stem: file.mtime for file in userscripts_dir.files()}
        self._watcher = watcher = qt.QFileSystemWatcher([userscripts_dir])
        watcher.directoryChanged.connect(self._reload_userscripts)

    def _setup_ui(self):
        # status bar
        self._status = status = StatusBar(self)
        self.setStatusBar(status)
        @status._search_changed
        def _(text):
            if viewer := self._stack.currentWidget():
                viewer._page.findText(text)

        # main widget
        self._widget = widget = qt.QWidget(self)
        layout = qt.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._tree = tree = TreeWidget(self)
        @tree.itemClicked
        def _(item):
            if data := item.data(0, Qt.UserRole):
                self._stack._open(data)
        @tree._letter_pressed
        def _(text):
            ic(text)
            if index := self._stack.currentWidget()._index:
                index._search(text)
        layout.addWidget(tree)

        self._stack = stack = StackWidget()
        stack._title_changed.connect(self._update_title)
        stack._doc_changed.connect(self._status._set_doc)
        stack._url_changed.connect(self._status._set_url)
        layout.addWidget(stack, 1)

        self.setCentralWidget(widget)

        # open first document to prevent flashing
        tree.setCurrentItem(tree.topLevelItem(0))
        stack._open(tree.topLevelItem(0).data(0, Qt.UserRole))

    def keyPressEvent(self, event):
        # uppercase letter is determined by shift key, the code is the same with the lowercase letter
        if Qt.Key_A <= event.key() <= Qt.Key_Z and event.modifiers() == Qt.NoModifier:
            self._search_index(event.text())
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        settings['window.geometry'] = self.saveGeometry()
        # settings['window.dock'] = self._dock_manager.saveState()

        stack = self._stack
        for i in range(stack.count()):
            stack.widget(i)._cleanup()

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

    @property
    def _current_page(self):
        return self._stack.currentWidget()._page

    def _trigger_action(self, action):
        self._current_page.triggerAction(getattr(qt.QWebEnginePage.WebAction, action))

    def _search_index(self, text):
        if index := self._stack.currentWidget()._index:
            index._search(text)

    def _update_title(self, title):
        if item := self._tree.currentItem():
            self.setWindowTitle(f'{item.text(0)} | {title}')

    def _reload_userscripts(self, path):
        userscripts = self._userscripts
        stack = self._stack
        widgets = {}
        for i in range(stack.count()):
            w = stack.widget(i)
            widgets[w._name] = w

        names = set()
        for file in Path(path).files():
            if file.size > 0:
                name = file.stem
                if name not in userscripts or file.mtime > userscripts[name]:
                    ic('reload userscript', file)
                    widgets[name]._set_userscript(file)
                    userscripts[name] = file.mtime
                names.add(name)

        for name in userscripts.keys():
            if name not in names:
                ic('remove userscript', name)
                widgets[name]._remove_userscript()

    def _search(self):
        input = self._status._search
        input.setFocus(Qt.MouseFocusReason)
        if input.text():
            input.selectAll()

    def _search_next(self):
        input = self._status._search
        if text := input.text().strip():
            if viewer := self._stack.currentWidget():
                viewer._page.findText(text)

    def _search_prev(self):
        input = self._status._search
        if text := input.text().strip():
            if viewer := self._stack.currentWidget():
                viewer._page.findText(text, qt.QWebEnginePage.FindFlag.FindBackward)

    def _search_clear(self):
        if viewer := self._stack.currentWidget():
            viewer._page.findText('')

    def _set_baseline(self):
        if viewer := self._stack.currentWidget():
            if viewer._doc.format == 'mirror':
                viewer._doc.set_prop('baseline', utils.epoch())
                viewer._doc.__getitem__.cache_clear()
                self._status._set_doc(viewer._doc)
