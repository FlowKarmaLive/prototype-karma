#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Copyright © 2016 Simon Forman
#
#	This file is part of MemeStreamer.
#
#	MemeStreamer is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	MemeStreamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with MemeStreamer.  If not, see <http://www.gnu.org/licenses/>.
#
from argparse import ArgumentParser
from os.path import abspath, exists
from server import run
import stores


def main(log, argv=None):
	args = get_args(argv)
	db_file = abspath(args.db_file)
	create_tables = not exists(db_file)
	if create_tables:
		log.info('DB file %r not found, creating.' % db_file)
	stores.connect(db_file, create_tables)
	run(host=args.host, port=args.port)


def make_argparser():
	parser = ArgumentParser(
		prog='MemeStreamer',
		description='Run the MemeStreamer server.',
		)
	parser.add_argument(
		'--db-file',
		type=str,
		help='The SQLite database file . (Default: ./memestreamer.sqlite)',
		default='./memestreamer.sqlite',
		)
	parser.add_argument(
		'--host',
		type=str,
		help='The host (IP) to bind. Default: localhost.',
		default='localhost',
		)
	parser.add_argument(
		'--port',
		type=int,
		help='The port number on which to listen. Default: 8000.',
		default=8000,
		)
	return parser


def get_args(argv=None):
	if argv is None:
		import sys
		argv = sys.argv[1:]
	return make_argparser().parse_args(argv)
