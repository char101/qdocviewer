import os
import sys

import colorama
import icecream
import pygments
from path import Path

from . import qt

sys.path.append(Path(__file__).parent / r'rapidfuzz\_skbuild\win-amd64-3.12\cmake-install\src')

if sys.platform == 'win32':
    colorama.just_fix_windows_console()

try:
    try:
        columns = os.get_terminal_size().columns
        icecream.icecream.IceCreamDebugger.lineWrapWidth = columns - 4
    except OSError:
        pass
    icecream.colorize.formatter = pygments.formatters.Terminal256Formatter(style='native')
except OSError:
    pass
icecream.ic.configureOutput(
    includeContext=True,
    outputFunction=lambda s: print(icecream.colorize(s), file=sys.stdout),
)
icecream.install()

sys.excepthook = qt.excepthook

app = qt.QApplication(sys.argv)
app.setStyle('fusion')
app.setWindowIcon(qt.QIcon(Path(__file__).parent / 'app.png'))
app.setStyleSheet("""
    QScrollBar:vertical, QScrollBar:horizontal { background: #525252 }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background: #696969; }
""")

try:
    from .mainwindow import MainWindow
except Exception as err:
    import ctypes
    import traceback

    ctypes.windll.user32.MessageBoxW(None, ''.join(traceback.format_exception(err, limit=5)), str(err), 0)
    sys.exit(0)

win = MainWindow()
win.show()

try:
    app.exec()
except KeyboardInterrupt:
    pass
except Exception as err:
    print(err)
    sys.exit(0)
