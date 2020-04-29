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
from wsgiref.simple_server import make_server
from server import Server
import stores


def main(log, argv=None):
	args = get_args(argv)

	static_files = abspath(args.static_files)
	if not exists(static_files):
		message = 'static_files dir %r does not exist.' % static_files
		log.error(message)
		raise ValueError(message)

	db_file = abspath(args.db_file)
	create_tables = not exists(db_file)
	if create_tables:
		log.info('DB file %r not found, creating.' % db_file)
	stores.connect(db_file, create_tables)
	
	server = Server(log, static_files)
	run(server, args.host, args.port)


def make_argparser():
	parser = ArgumentParser(
		prog='MemeStreamer',
		description='Run the MemeStreamer server.',
		)
	parser.add_argument(
		'--static-files',
		type=str,
		help='The directory containing web content files. (Default: ./web)',
		default='./web',
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
		default='',
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


def run(app, host='', port=8000):
	httpd = make_server(host, port, app)
	_print_serving(host, port)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass


def _print_serving(host, port):
	print(
		'server at http://%s:%i/'
		% (host or 'localhost', port)
		)
