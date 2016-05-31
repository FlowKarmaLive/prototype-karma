from sqlitey import get_tag, write_tag, get_conn, T
from stores import SQLITE_DB


conn = get_conn(SQLITE_DB)
c = conn.cursor()

print 'tagged URLs'
c.execute('select when_, tag, url FROM tags')
for when_, tag_, url_ in c.fetchall():
  print when_, tag_, url_

print
print 'bumps'
c.execute('select * FROM bumps')
for row in c.fetchall():
  print row
