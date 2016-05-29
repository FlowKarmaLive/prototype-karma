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
from os import makedirs
from os.path import exists, join
from traceback import format_exc
from html import (
  ok200,
  err500,
  HTML,
  fake_out_caching,
  labeled_field,
  labeled_textarea,
  posting,
  )


class Server(object):

  def __init__(self, log):
    self.log = log
    self._router = {
      '/': self.root,
      'register': self.register,
      }
    self.debug = False

  def root(self, environ):
    return home_page()

  def register(self, environ):
    if not posting(environ):
      return self.root(environ)  # Poor man's redirect to home...
    form = self._enformenate(environ)
    url = form.getfirst('url')
    return url

  def handle_request(self, environ, start_response):
    path = self.route(environ)
    handler = self._router.get(path, self.default_handler)
    response = handler(environ)
    return ok200(start_response, response)

  def route(self, environ):
    path = environ['PATH_INFO']
    if path.startswith('/register'):
      return 'register'
    return path

  def default_handler(self, environ):
    path = self.route(environ)
    msg = 'You chose: ' + repr(path)
    self.log.debug(msg)
    return msg

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


def home_page():
  doc = HTML()
  doc.head
  with doc.body as body:
    body.hr
    with body.form(action='/register', method='POST') as form:
      form.h4('Register')
      labeled_field(
        form,
        'URL:',
        'text',
        'url',
        '',
        size='44',
        placeholder='Enter an URL here...',
        )
      form.br
      labeled_textarea(
        form,
        'Description:',
        'description',
        '',
        cols='58',
        rows='15',
        placeholder='Describe what this URL links to...',
        )
      form.br
      fake_out_caching(form)
      form.input(type_='submit', value='post')
  return str(doc)

