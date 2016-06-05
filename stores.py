# -*- coding: utf-8 -*-
#
#    Copyright © 2016 Simon Forman
#
#    This file is part of MemeStreamer.
#
#    MemeStreamer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MemeStreamer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with MemeStreamer.  If not, see <http://www.gnu.org/licenses/>.
#
import logging
from urlparse import urlparse
from sqlitey import get_tag, write_tag, get_conn, bumpdb, engagedb, T
from tagly import tag_for


log = logging.getLogger('mon.db')
conn = None


def connect(db_file, create_tables):
  global conn
  if conn:
    raise RuntimeError('DB already connected %r', conn)
  conn = get_conn(db_file, create_tables)


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


def engage(receiver, it):
  c, t = conn.cursor(), T()
  try:
    result = engagedb(c, t, receiver, it)
  finally:
    c.close()
  if result:
    conn.commit()
    return result
  log.debug('duplicate engage %s %s', receiver, it)


def url2tag(url_):
  url = normalize_url(url_)
  if not url:
    log.debug('Not normalized URL %r', url_)
    raise ValueError('Not normalized URL %r' % (url_,))

  c, t, tag = conn.cursor(), T(), tag_for(url)
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
