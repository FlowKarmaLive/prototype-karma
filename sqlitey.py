# -*- coding: utf-8 -*-
#
#    Copyright © 2016, 2020, 2021 Simon Forman
#
#    This file is part of FlowKarma.Live.
#
#    FlowKarma.Live is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    FlowKarma.Live is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with FlowKarma.Live.  If not, see <http://www.gnu.org/licenses/>.
#
from time import time
import sqlite3
from tagly import tag_for


def get_conn(db=':memory:', create=False):
	conn = sqlite3.connect(db)
	conn.row_factory = VisibleRow
	if create:
		create_tables(conn)
	return conn


CREATE_TABLES = '''\
create table bumps (when_ INTEGER, key TEXT PRIMARY KEY, from_ TEXT, what TEXT, to_ TEXT)
create table tags (when_ INTEGER, tag TEXT PRIMARY KEY, user_ID TEXT, url TEXT)
create table engages (when_ INTEGER, key TEXT PRIMARY KEY, who TEXT, what TEXT)
create table users (when_ INTEGER, key TEXT PRIMARY KEY, profile TEXT, lineage TEXT)
'''.splitlines(False)


def create_tables(conn):
	c = conn.cursor()
	for statement in CREATE_TABLES:
		c.execute(statement)
	c.close()
	conn.commit()


def get_user_profile_db(c, user_ID):
	c.execute('select profile from users where key=?', (user_ID,))
	result = c.fetchone()
	return result[0] if result else None


def put_user_profile_db(c, user_ID, profile):
	c.execute(
		'update users set profile=? where key=?',
		(profile, user_ID)
		)


def write_tag(c, when, tag, user_ID, url):
	return insert(
		c,
		'insert into tags values (?, ?, ?, ?)',
		when,
		tag,
		user_ID,
		url,
		)


def get_tag(c, tag):
	c.execute('select user_ID, url from tags where tag=?', (tag,))
	return c.fetchone()


def bumpdb(c, when, from_, what, to):
	key = tag_for('%s:%s' % (what, to))
	return insert(
		c,
		'insert into bumps values (?, ?, ?, ?, ?)',
		when, key, from_, what, to,
		)


def engagedb(c, when, who, what):
	key = tag_for('%s:%s' % (who, what))
	return key if insert(
		c,
		'insert into engages values (?, ?, ?, ?)',
		when, key, who, what,
		) is not None else None


def extract_graph(c, tag):
	c.execute('select when_, from_, to_ FROM bumps WHERE what=?', (tag,))
	nodes, links = set(), []
	for when, from_, to in c.fetchall():
		nodes.update((from_, to))
		links.append((when, from_, to))
	return list(nodes), links


def insert(c, query, *values):
	try:
		c.execute(query, values)
	except sqlite3.IntegrityError:
		return
	return c.lastrowid


class VisibleRow(sqlite3.Row):
	def __str__(self):
		return str(tuple(self))
	__repr__ = __str__


def T():
	return int(round(time(), 3) * 1000)
