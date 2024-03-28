import yaml
from path import Path

from . import DOCS_DIR, Qt, qt, settings, utils
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
                Qt.Key_Left: lambda: self._trigger_action('Back'),
                Qt.Key_Right: lambda: self._trigger_action('Forward'),
                Qt.Key_F5: lambda: self._trigger_action('Reload'),
            },
        )

        userscripts_dir = DOCS_DIR / '_userscripts'
        self._userscripts = {file.stem: file.mtime for file in userscripts_dir.files()}
        self._watcher = watcher = qt.QFileSystemWatcher([userscripts_dir])
        watcher.directoryChanged.connect(self._reload_userscripts)

    def _load_docs(self):
        tree = self._tabs

        def load(items, parent=None):
            for name, params in items.items():
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

    @property
    def _current_page(self):
        return self._tabs._stack.currentWidget()._page

    def _trigger_action(self, action):
        self._current_page.triggerAction(getattr(qt.QWebEnginePage.WebAction, action))

    def _search_index(self, text):
        if index := self._tabs._stack.currentWidget()._index:
            index._search(text)

    def _update_title(self, title):
        if item := self._tabs._tree.currentItem():
            self.setWindowTitle(f'{item.text(0)} | {title}')

    def _reload_userscripts(self, path):
        userscripts = self._userscripts
        stack = self._tabs._stack
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
