from path import Path

from .qt import QMimeDatabase, Qt
from .sqlite import Db, Settings

APP_DIR = Path(__file__).parent
DOCS_DIR = APP_DIR / 'docs'
DATA_DIR = APP_DIR / 'data'

sqlite = Db(DATA_DIR)
settings = Settings(sqlite)
mime_db = QMimeDatabase()
