#from memcache import Client
import logging
from urlparse import urlparse
from sqlitey import get_tag, write_tag, get_conn, bumpdb, SQLITE_DB, T
from tagly import tag_for


log = logging.getLogger('mon.db')


#U2T = Client(['127.0.0.1:11213'], debug=True)
#T2U = Client(['127.0.0.1:11214'], debug=True)
conn = get_conn(SQLITE_DB)


def bump(sender, it, receiver):
  c, t = conn.cursor(), T()
  try:
    result = bumpdb(c, t, sender, it, receiver)
  finally:
    c.close()
  if result:
    conn.commit()
    return True
  log.debug('duplicate bump %s %s %s', sender, it, receiver)


def url2tag(url_):
  url = normalize_url(url_)
  if not url:
    log.debug('Not normalized URL %r', url_)
    raise ValueError('Not normalized URL %r' % (url_,))

  c, t, tag, result = conn.cursor(), T(), tag_for(url), None
  try:
    result = write_tag(c, t, tag, url)
  finally:
    c.close()

  if result:
    conn.commit()
    log.debug('Wrote %s %s', tag, url)
  else:
    log.debug('Already tagged %s %s', tag, url)

  return bool(result), tag


def tag2url(tag):
  c = conn.cursor()
  try:
    url = get_tag(c, tag)
  finally:
    c.close()
  if url:
    log.debug('Found %s %s', tag, url)
    return url
  log.debug('Missed %s', tag)
  raise KeyError(tag)


##def url2tag(url):
##  url = str(url)
##  tag = U2T.get(url)
##  if not tag:
##    tag = tag_for(url)
##    U2T.set(url, tag)
##    T2U.set(tag, url)
##  return tag


##def tag2url(tag):
##  tag = str(tag)
##  url = T2U.get(tag)
##  if not url:
##    raise KeyError(tag)
##  return url

def normalize_url(url):
  try:
    url = str(url)
    url = url.lower()
    result = urlparse(url)
  except:
    log.exception('While parsing URL %r', url)
    return
  if (result.scheme in ('http', 'https')
      and not (result.params or result.query or result.fragment)):
    return result.geturl()
