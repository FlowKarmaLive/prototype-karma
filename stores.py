from memcache import Client
from tagly import tag_for


U2T = Client(['127.0.0.1:11213'], debug=True)
T2U = Client(['127.0.0.1:11214'], debug=True)


def url2tag(url, log):
  url = str(url)
  tag = U2T.get(url)
  if not tag:
    tag = tag_for(url)
    log.info('register %s %r', tag, url)
    U2T.set(url, tag)
    T2U.set(tag, url)
  return tag


def tag2url(tag):
  tag = str(tag)
  url = T2U.get(tag)
  if not url:
    raise KeyError(tag)
  return url

