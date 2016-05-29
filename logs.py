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


F = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')


def setup_log():
  log = logging.getLogger('mon')
  log.setLevel(logging.DEBUG)

  sh = logging.StreamHandler()
  sh.setLevel(logging.DEBUG)
  sh.setFormatter(F)
  log.addHandler(sh)

  fh = logging.FileHandler('memestreamer.log')
  fh.setLevel(logging.DEBUG)
  fh.setFormatter(F)
  log.addHandler(fh)

  return log

