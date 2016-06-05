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
  '''
  A simple WSGI server that handles both static resources and API calls.
  '''

  def __init__(self, log, static_dir):
    self.log = log.getChild('record')  # For "events".
    self.err_log = log.getChild('error')

    self.static_dir = static_dir  # Location of templates and static files.

    self.api_methods = {'register', 'bump', 'engage'}

    self.debug = False  # Set True if running in e.g. pdb or something.

    # Pre-load templates.
    self.home_template = self._read_template('index.html')
    self.bump_template = self._read_template('bump.html')
    self.bump_anon_template = self._read_template('bump_anon.html')
    self.register_template = self._read_template('register.html')

  def __call__(self, environ, start_response):
    if self.debug:  # Let the calling context handle exceptions.
      return self.handle_request(environ, start_response)
    try:
      return self.handle_request(environ, start_response)
    except:  # Uncaught exceptions become 500 errors.
      self.err_log.exception('problem in handle_request')
      return err500(start_response, format_exc())

  def handle_request(self, environ, start_response):
    path = environ['PATH_INFO'].lstrip('/')
    if not path:  # Serve homepage.
      return ok200(start_response, self.home_template)
    selector = path.partition('/')[0]

    # Serve static assets.
    if selector == 'static':
      filename = join(self.static_dir, path)
      if not exists(filename):
        return err404(start_response)
      start(start_response, '200 OK', guess_type(path))
      return file(filename, 'rb')

    # Handle API calls.
    if selector in self.api_methods:
      handler = getattr(self, selector)
      response = handler(environ)
      return ok200(start_response, response)
    return err404(start_response)

  def register(self, environ):
    '''
    Accept an URL and return its tag, enter a register record in the DB
    if this is the first time we've seen this URL.
    '''
    if not posting(environ):
      return self.register_template
    url = self._enformenate(environ).getfirst('urly')
    unseen, tag = url2tag(url)
    if unseen:
      self.log.info('register %s %r', tag, url)
    return tag

  def bump(self, environ):
    '''
    Record the connection between two nodes in re: a "meme" URL.
    '''
    if posting(environ):
      # There used to be a form on the homepage that let you just enter
      # three URLs and POST to do a bump, for debugging.  This is legacy
      # from that and could be removed (no POST bumps.)
      form = self._enformenate(environ)
      sender, it, receiver = map(form.getfirst, ('sender', 'it', 'receiver'))
    else:
      sender, it, receiver = self._decode_bump(environ['PATH_INFO'])

    if not receiver:
      return self.bump_anon(sender, it)

    data = dict(
      from_url=tag2url(sender),
      iframe_url=tag2url(it),
      your_url=tag2url(receiver),
      me=sender,
      it=it,
      you=receiver,
      server='localhost:8000',  # FIXME!!
      )
    if bump(sender, it, receiver):
      self.log.info('bump %s %s %s', sender, it, receiver)
    return self.bump_template % data

  def _decode_bump(self, path):
    '''
    Bump URLS look like:

      /bump/<sender>/<it>/<receiver>

    Or "anon" URLs:

      /bump/<sender>/<it>

    The trailing slash is optional.
    '''
    parts = path.strip('/').split('/')
    if parts.pop(0) != 'bump':
      raise ValueError('Bad bump for bump %r' % (path,))
    if len(parts) == 2: (sender, it), receiver = parts, None
    elif len(parts) == 3: sender, it, receiver = parts
    else:
      raise ValueError('Bad path for bump %r' % (path,))
    return sender, it, receiver

  def bump_anon(self, sender, it):
    '''
    Send an "anonymous" bump page, allowing new people to join the network.

    If the user already has an "own_tag" cookie the page will affix the
    user's tag to the anon bump URL and load the resulting bump URL.
    '''
    data = dict(
      from_url=tag2url(sender),
      iframe_url=tag2url(it),
      me=sender,
      it=it,
      server='localhost:8000',  # FIXME!!
      )
    return self.bump_anon_template % data

  def engage(self, environ):
    '''
    Record the "engagement" of a user with some meme.

    Eventually this will generate some sort of correlation code that we
    return to the calling page which then passes it to the meme URL as a
    parameter letting whoever's on the other know who to thank.
    '''
    path = environ['PATH_INFO']
    parts = path.strip('/').split('/')
    try:
      receiver, it = parts[1:]
    except ValueError:
      raise ValueError('Bad path for engage %r' % (path,))
    tag2url(receiver) ; tag2url(it)  # crude validation
    key = engage(receiver, it)
    if key:
      self.log.info('engage key:%s %s %s', key, receiver, it)
    return 'engaged'

  def _enformenate(self, environ):
    '''Return FieldStorage object for the request.'''
    environ['QUERY_STRING'] = ''  # I forget why.
    return FieldStorage(
      fp=environ['wsgi.input'],
      environ=environ,
      keep_blank_values=True,
      )

  def _read_template(self, filename):
    with open(join(self.static_dir, filename), 'rb') as template:
      data = template.read()
    return data
