from sqlitey import get_tag, write_tag, get_conn, T


conn = get_conn('./memestreamer.sqlite')
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
