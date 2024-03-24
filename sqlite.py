import datetime
import os
import pickle
import sqlite3

from path import Path

DB_DIR = Path(__file__).parent
SQLS_DIR = Path(__file__).parent / 'sql'


class Row(sqlite3.Row):
    def __getattr__(self, name):
        return self[name]


sqlite3.register_adapter(datetime.datetime, lambda dt: dt.isoformat(' ', 'seconds'))


def connect(path, **kwargs):
    conn = sqlite3.connect(path, **kwargs)
    conn.executescript('pragma journal_mode = WAL; pragma synchronous = off; pragma temp_store = memory;')
    return conn


class Db:
    def __init__(self, dbPath):
        if os.path.isdir(dbPath):
            dbPath = os.path.join(dbPath, 'data.sqlite')
        elif dbPath.endswith('.py'):
            dbPath = os.path.join(os.path.dirname(dbPath), 'data.sqlite')
        conn = connect(dbPath)
        conn.row_factory = Row
        curr = conn.cursor()
        curr.execute('create table if not exists setting (key text not null primary key, value blob)')
        self.conn = conn
        self.curr = curr
        self.level = 0

    def sql(self, name, **params):
        sql = (SQLS_DIR / f'{name}.sql').text()
        if params:
            sql = sql.format(**params)
        return sql

    def execute(self, sql, params=()):
        if not isinstance(params, (list, tuple)):
            params = (params,)
        self.curr.execute(sql, params)

    def row(self, sql, params=()):
        self.execute(sql, params)
        return self.curr.fetchone()

    def all(self, sql, params=()):
        self.execute(sql, params)
        return self.curr.fetchall()

    def col(self, sql, params=()):
        return [row[0] for row in self.all(sql, params)]

    def set(self, sql, params=()):
        return set(row[0] for row in self.all(sql, params))

    def map(self, sql, params=()):
        data = self.all(sql, params)
        if not data:
            return {}
        if len(data[0]) == 2:
            return {row[0]: row[1] for row in data}
        return {row[0]: row for row in data}

    def columns(self, sql, params=()):
        data = self.all(sql, params)
        columns = {col[0]: [] for col in self.curr.description}
        for row in data:
            for col, values in columns.items():
                values.append(getattr(row, col))
        return columns

    def one(self, sql, params=()):
        row = self.row(sql, params)
        if row:
            return row[0]
        return None

    def where(self, params):
        w = []
        for k, v in params.items():
            if v is None:
                w.append(f'{k} is null')
            else:
                w.append(f'{k} = {v}')
        return ' where ' + ' and '.join(w) + ' '

    def insert(self, table, params, returning=None):
        bind = []
        cols = []
        vals = []
        for k, v in params.items():
            cols.append(k)
            bind.append('?')
            vals.append(v)
        cols = ', '.join(cols)
        bind = ', '.join(bind)
        sql = 'insert into {} ({}) values ({})'.format(table, cols, bind)

        if returning:
            sql += ' returning ' + returning
            return self.one(sql, vals)

        return self.curr.execute(sql, vals)

    def update(self, table, update, where, params=None):
        if params is None:
            params = []
        if isinstance(update, dict):
            params.extend(update.values())
            update = ', '.join(f'{k} = ?' for k in update.keys())
        if isinstance(where, dict):
            params.extend(where.values())
            where = ' and '.join(f'{k} = ?' for k in where.keys())
        return self.curr.execute(f'update {table} set {update} where {where}', params)

    def upsert(self, table, data):
        columns = []
        binds = []
        params = []
        updates = []
        for k, v in data.items():
            if k[0] == '*':
                k = k[1:]
                key = k
            columns.append(k)
            binds.append('?')
            params.append(v)
            if k != key:
                updates.append(f'{k} = excluded.{k}')
        columns = ', '.join(columns)
        binds = ', '.join(binds)
        updates = ', '.join(updates)
        return self.curr.execute(f'insert into {table} ({columns}) values ({binds}) on conflict ({key}) do update set {updates}', params)

    def delete(self, table, where, params=None):
        if isinstance(where, dict):
            params = tuple(where.values())
            where = ' and '.join(f'{k} = ?' for k in where.keys())
        return self.curr.execute(f'delete from {table} where {where}', params)

    def exists(self, table, where):
        if isinstance(where, dict):
            params = tuple(where.values())
            where = ' and '.join(f'{k} = ?' for k in where.keys())
        return self.one(f'select exists (select 1 from {table} where {where})', params)

    def __enter__(self):
        self.level += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.level -= 1
        if exc_type is None and self.level == 0:
            self.conn.commit()


class Settings:
    def __init__(self, db):
        self.db = db
        self.data = {key: value for key, value in db.all('select key, value from setting')}

    def __getitem__(self, key):
        if key in self.data:
            return pickle.loads(self.data[key])
        return None

    def __setitem__(self, key, value):
        value = pickle.dumps(value)
        with self.db:
            if key in self.data:
                if value != self.data[key]:
                    self.db.update('setting', {'value': value}, {'key': key})
            else:
                self.db.insert('setting', {'key': key, 'value': value})
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def get(self, key, default=None):
        if key in self.data:
            try:
                return pickle.loads(self.data[key])
            except ImportError:
                pass
        return default
