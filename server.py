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
from cgi import FieldStorage
from traceback import format_exc
from html import (
  ok200,
  err500,
  HTML,
  fake_out_caching,
  labeled_field,
  labeled_textarea,
  posting,
  static_page,
  )
from stores import url2tag, tag2url, bump


class Server(object):

  def __init__(self, log):
    self.log = log
    self._router = {
      '/': self.root,
      'register': self.register,
      'bump': self.bump,
      }
    self.debug = False

  def root(self, environ):
    return home_page()

  def register(self, environ):
    if not posting(environ):
      return self.root(environ)  # Poor man's redirect to home...
    form = self._enformenate(environ)
    url = form.getfirst('url')
    unseen, tag = url2tag(url)
    if unseen:
      self.log.info('register %s %r', tag, url)
    return reg_happiness_page(url, tag)

  def bump(self, environ):
    if not posting(environ):
      return self.root(environ)  # Poor man's redirect to home...
    form = self._enformenate(environ)
    sender = form.getfirst('sender')
    from_url = tag2url(sender)
    it = form.getfirst('it')
    iframe_url = tag2url(it)
    receiver = form.getfirst('receiver')
    your_url = tag2url(receiver)
    if bump(sender, it, receiver):
      self.log.info('bump %s %s %s', sender, it, receiver)
    return bump_page(
      sender, from_url,
      it, iframe_url,
      receiver, your_url,
      )

  def handle_request(self, environ, start_response):
    path = self.route(environ)
    handler = self._router.get(path, self.default_handler)
    response = handler(environ)
    return ok200(start_response, response)

  def route(self, environ):
    path = environ['PATH_INFO']
    if path.startswith('/register'):
      return 'register'
    if path.startswith('/bump'):
      return 'bump'
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


def reg_happiness_page(url, tag):
  doc = HTML()
  doc.head
  with doc.body as body:
    body += 'Tag'
    body.h4(tag)
    body += 'for URL'
    body.h4(url)
  return str(doc)


def bump_page(sender, from_url, it, iframe_url, receiver, your_url):
  doc = HTML()
  doc.head
  with doc.body as body:
    body += 'Sent from: ' + from_url
    body.br
    body += 'Sent to: ' + your_url
    body.br
    body += 'It is: '
    body.a(iframe_url, href=iframe_url)
  return str(doc)


@static_page
def home_page():
  doc = HTML()
  doc.head
  with doc.body as body:
    body.hr
    with body.form(action='/register', method='POST') as form:
      form.h4('Register')
      labeled_field(form, 'URL:', 'text', 'url', '', size='44', placeholder='Enter an URL here...')
      form.br
      fake_out_caching(form)
      form.input(type_='submit', value='post')
    body.hr
    with body.form(action='/bump', method='POST') as form:
      form.h4('Bump')
      labeled_field(form, 'from:', 'text', 'sender', '', size='44', placeholder='Enter an URL here...')
      form.br
      labeled_field(form, 'to:', 'text', 'receiver', '', size='44', placeholder='Enter an URL here...')
      form.br
      labeled_field(form, 'what:', 'text', 'it', '', size='44', placeholder='Enter an URL here...')
      form.br
      fake_out_caching(form)
      form.input(type_='submit', value='post')
    body.hr

  return str(doc)
