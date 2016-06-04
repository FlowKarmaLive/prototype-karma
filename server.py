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
import mimetypes
from os.path import splitext, join, exists
from cgi import FieldStorage
from traceback import format_exc
from http import ok200, err404, err500, posting, start
from stores import url2tag, tag2url, bump, engage


if not mimetypes.inited: mimetypes.init()
extensions_map = mimetypes.types_map.copy()
extensions_map[''] = 'application/octet-stream'


def guess_type(path):
  ext = splitext(path)[1].lower()
  return extensions_map.get(ext, 'application/octet-stream')


class Server(object):

  def __init__(self, log, static_dir):
    self.log = log
    self.static_dir = static_dir
    self._router = {
      '/': self.root,
      'register': self.register,
      'bump': self.bump,
      'engage': self.engage,
      }
    self.debug = False
    self.home_template = self._read_template('index.html')
    self.bump_template = self._read_template('bump.html')
    self.bump_anon_template = self._read_template('bump_anon.html')
    self.register_template = self._read_template('register.html')

  def root(self, environ):
    return self.home_template

  def register(self, environ):
    if not posting(environ):
      return self.register_template
    form = self._enformenate(environ)
    url = form.getfirst('urly')
    unseen, tag = url2tag(url)
    if unseen:
      self.log.info('register %s %r', tag, url)
    return tag

  def bump(self, environ):
    if not posting(environ):
      sender, it, receiver = self.decode_bump(environ['PATH_INFO'])
      if not receiver:
        return self.bump_anon(sender, it)
    else:
      form = self._enformenate(environ)
      sender, it, receiver = map(form.getfirst, ('sender', 'it', 'receiver'))
    data = dict(
      from_url=tag2url(sender),
      iframe_url=tag2url(it),
      your_url=tag2url(receiver),
      me=sender,
      it=it,
      you=receiver,
      server='localhost:8000',
      )
    if bump(sender, it, receiver):
      self.log.info('bump %s %s %s', sender, it, receiver)
    return self.bump_template % data

  def decode_bump(self, path):
    parts = path.strip('/').split('/')
    if parts.pop(0) != 'bump':
      self.log.debug('Bad bump for bump %r', path)
      raise ValueError('Bad bump for bump %r' % (path,))
    if len(parts) == 2:
      (sender, it), receiver = parts, None
    elif len(parts) == 3:
      sender, it, receiver = parts
    else:
      self.log.debug('Bad path for bump %r', path)
      raise ValueError('Bad path for bump %r' % (path,))
    return sender, it, receiver

  def bump_anon(self, sender, it):
    data = dict(
      from_url=tag2url(sender),
      iframe_url=tag2url(it),
      me=sender,
      it=it,
      server='localhost:8000',
      )
    return self.bump_anon_template % data

  def engage(self, environ):
    path = environ['PATH_INFO']
    parts = path.strip('/').split('/')
    if parts.pop(0) != 'engage':
      self.log.debug('Bad engage for engage %r', path)
      raise ValueError('Bad engage for engage %r' % (path,))
    try:
      receiver, it = parts
    except ValueError:
      self.log.debug('Bad path for engage %r', path)
      raise ValueError('Bad path for engage %r' % (path,))
    tag2url(receiver) ; tag2url(it)  # crude validation
    key = engage(receiver, it)
    if key:
      self.log.info('engage key:%s %s %s', key, receiver, it)
    return 'engaged'

  def handle_request(self, environ, start_response):
    path = environ['PATH_INFO']

    # Serve static assets.
    if path.startswith('/static/'):
      filename = join(self.static_dir, path[1:])
      if not exists(filename):
        return err404(start_response)
      start(start_response, '200 OK', guess_type(path))
      return file(filename, 'rb')

    # Handle API calls.
    path = self.route(environ)
    handler = self._router.get(path)
    if not handler:
      return err404(start_response)
    response = handler(environ)
    return ok200(start_response, response)

  def route(self, environ):
    path = environ['PATH_INFO']
    if path.startswith('/register'):
      return 'register'
    if path.startswith('/bump'):
      return 'bump'
    if path.startswith('/engage'):
      return 'engage'
    return path

  def __call__(self, environ, start_response):
    if self.debug:
      return self.handle_request(environ, start_response)
    try:
      return self.handle_request(environ, start_response)
    except:
      return err500(start_response, format_exc())

  def _enformenate(self, environ):
    environ['QUERY_STRING'] = ''
    return FieldStorage(
      fp=environ['wsgi.input'],
      environ=environ,
      keep_blank_values=True,
      )

  def _read_template(self, filename):
    with open(join(self.static_dir, filename), 'rb') as template:
      data = template.read()
    return data
