from sqlitey import get_tag, write_tag, get_conn, SQLITE_DB, MAKE_TABLES, T


conn = get_conn(SQLITE_DB, MAKE_TABLES)
c = conn.cursor()

c.execute('select when_, tag, url FROM tags')
for when_, tag_, url_ in c.fetchall():
  print when_, tag_, url_
