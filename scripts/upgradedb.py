import sqlite3

from path import Path


class DB:
    def __init__(self, conn):
        self.conn = conn
        self.curr = conn.cursor()

    def execute(self, query, params=()):
        return self.curr.execute(query, params)

    def get_one(self, query, params=()):
        self.curr.execute(query, params)
        row = self.curr.fetchone()
        if row:
            return row[0]

    def get_row(self, query, params=()):
        self.curr.execute(query, params)
        return self.curr.fetchone()

    def get_all(self, query, params=()):
        self.curr.execute(query, params)
        return self.curr.fetchall()

    def has_column(self, table, column):
        for row in self.get_all(f"pragma table_info('{table}')"):
            if row[1] == column:
                return True
        return False

    def close(self):
        self.conn.close()


for file in Path('docs').walkfiles():
    if file.name == 'cache.sqlite':
        print(file)
        db = DB(sqlite3.connect(file, autocommit=True))

        # v2
        # if not db.has_column('cache', 'updated'):
        #     db.execute('alter table cache rename column created to updated')
        # if not db.has_column('cache', 'refresh'):
        #     db.execute('alter table cache add column refresh integer default 0 not null')

        db.execute('vacuum')
        db.close()
