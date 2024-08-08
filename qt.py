import os
import traceback
from enum import EnumType

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import *
from PyQt6.sip import wrappertype

for obj in tuple(globals().values()):
    if isinstance(obj, wrappertype):
        for attr in tuple(obj.__dict__.values()):
            if isinstance(attr, EnumType):
                for k, v in attr.__members__.items():
                    if not hasattr(obj, k):
                        setattr(obj, k, v)

Signal = pyqtSignal
Slot = pyqtSlot

pyqtBoundSignal.__call__ = pyqtBoundSignal.connect

_is_quitting = False


def showError(title, text, last_traceback, traceback):
    print('showError:', title)
    print(text)
    print(''.join(last_traceback))
    mb = QMessageBox(QMessageBox.Icon.Critical, title, text, QMessageBox.StandardButton.Close)
    mb.setInformativeText(''.join(last_traceback))
    mb.setDetailedText(''.join(traceback))
    mb.setSizeGripEnabled(True)
    mb.setFixedWidth(600)
    mb.setFixedHeight(800)
    mb.setDefaultButton(QMessageBox.StandardButton.Close)
    mb.exec()
    print('mb closed')


def showException(exc, prefix=None):
    if isinstance(exc, tuple):
        type_, value, tb = exc
        title = f'[{prefix}] {type_}' if prefix else str(type_)
        showError(title, str(value), traceback.format_exception(type_, value, tb, limit=-5), traceback.format_exception(type_, value, tb))
    else:
        title = f'[{prefix}] {type(exc)}' if prefix else str(type(exc))
        showError(title, str(exc), traceback.format_exception(exc, limit=-5), traceback.format_exception(exc))


def showWarning(text, title=None):
    mb = QMessageBox(QMessageBox.Icon.Warning, title or 'Warning', text, QMessageBox.StandardButton.Ok, QApplication.activeWindow())
    mb.exec()


def excepthook(type, value, tb):
    global _is_quitting
    if not _is_quitting:
        _is_quitting = True
        window = QApplication.activeWindow()
        # close the mainwindow to prevent high cpu usage
        if window is not None:
            try:
                window.close()
            except Exception as err:
                print(err)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        if type != KeyboardInterrupt:
            showException((type, value, tb), prefix='excepthook')
        ic('exit here')
        app.exit(0)
        os._exit(0)


def setLastHwnd(hwnd):
    if isinstance(hwnd, QMainWindow):
        hwnd = int(hwnd.winId())
    with open(r'S:\qt\last_hwnd', 'w') as f:
        f.write(str(hwnd))
