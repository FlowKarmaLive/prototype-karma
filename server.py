#!/usr/bin/env python
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
from html import ok200, err500


class Server(object):

  def __init__(self):
    self._router = {}
    self.debug = False

  def handle_request(self, environ, start_response):
    path = self.route(environ)
    handler = self._router.get(path, self.default_handler)
    response = handler(environ)
    return ok200(start_response, response)

  def route(self, environ):
    return environ['PATH_INFO']

  def default_handler(self, environ):
    path = self.route(environ)
    return 'You chose: ' + path

  def __call__(self, environ, start_response):
    if self.debug:
      return self.handle_request(environ, start_response)
    try:
      return self.handle_request(environ, start_response)
    except:
      return err500(start_response, format_exc())

