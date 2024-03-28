from path import Path

from .qt import QMimeDatabase, Qt
from .sqlite import Db, Settings

APP_DIR = Path(__file__).parent
DOCS_DIR = APP_DIR / 'docs'
DATA_DIR = APP_DIR / 'data'
ICONS_DIR = APP_DIR / 'icons'
USERSCRIPTS_DIR = DOCS_DIR / '_userscripts'

db = Db(DATA_DIR)
settings = Settings(db)
mime_db = QMimeDatabase()
