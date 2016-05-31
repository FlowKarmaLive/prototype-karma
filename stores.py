import logging
from os.path import exists, expanduser
from urlparse import urlparse
from sqlitey import get_tag, write_tag, get_conn, bumpdb, T
from tagly import tag_for


log = logging.getLogger('mon.db')
SQLITE_DB = expanduser('~/memestreamer.sqlite')
conn = get_conn(SQLITE_DB, not exists(SQLITE_DB))


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


def normalize_url(url):
  try:
    url = str(url)
    result = urlparse(url)
  except:
    log.exception('While parsing URL %r', url)
    return
  if (result.scheme.lower() in ('http', 'https')
      and not (result.params or result.query or result.fragment)):
    return result.geturl()
