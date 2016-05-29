from time import time
from os.path import exists, expanduser
import sqlite3


SQLITE_DB = expanduser('~/memestreamer.sqlite')
MAKE_TABLES = not exists(SQLITE_DB)


def get_conn(db=':memory:', make_tables=False):
  conn = sqlite3.connect(db)
  conn.row_factory = VisibleRow
  if make_tables:
    print 'creating tables'
    create_tables(conn)
  return conn


CREATE_TABLES = '''\
create table bumps (when_ INTEGER, key TEXT PRIMARY KEY, from_ TEXT, what TEXT, to_ TEXT)
create table tags (when_ INTEGER, tag TEXT PRIMARY KEY, url TEXT)
'''.splitlines(False)


def create_tables(conn):
  c = conn.cursor()
  for statement in CREATE_TABLES:
    c.execute(statement)
  conn.commit()
  c.close()


def write_tag(c, when, tag, url):
  return insert(c, 'insert into tags values (?, ?, ?)', when, tag, url)


def get_tag(c, tag):
  tag = (tag,)
  c.execute('select url from tags where tag=?', tag)
  result = c.fetchone()
  return str(result[0]) if result else None


def bump(c, when, from_, what, to):
  key = '%s:%s' % (what, to)
  return insert(
    c,
    'insert into bumps values (?, ?, ?, ?, ?)',
    when, key, from_, what, to,
    )


def extract_graph(c, tag):
  c.execute('select when_, from_, to_ FROM bumps WHERE what=?', (tag,))
  nodes, links = set(), []
  for when, from_, to in c.fetchall():
    nodes.update((from_, to))
    links.append((when, from_, to))
  return list(nodes), links


def insert(c, query, *values):
  try:
    c.execute(query, values)
  except sqlite3.IntegrityError:
    return
  return c.lastrowid


class VisibleRow(sqlite3.Row):
  def __str__(self):
    return str(tuple(self))
  __repr__ = __str__


def T():
  return int(round(time(), 3) * 1000)


conn = get_conn(SQLITE_DB, MAKE_TABLES)
c = conn.cursor()
