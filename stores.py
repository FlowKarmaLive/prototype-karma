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
import logging, json
from urllib.parse import urlparse
from sqlitey import (
	bumpdb,
	engagedb,
	get_conn,
	get_tag,
	get_user_profile_db,
	put_user_profile_db,
	T,
	write_tag,
	)
from tagly import tag_for
from bottle import abort


log = logging.getLogger('mon.db')
conn = None


def connect(db_file, create_tables):
	global conn
	if conn:
		raise RuntimeError('DB already connected %r', conn)
	conn = get_conn(db_file, create_tables)


def bump(sender, it, receiver):
	c = conn.cursor()
	try:
		result = bumpdb(c, T(), sender, it, receiver)
	finally:
		c.close()
	if result:
		conn.commit()
		return True
	log.debug('duplicate bump %s %s %s', sender, it, receiver)
	return False


def engage(receiver, it):
	c = conn.cursor()
	try:
		result = engagedb(c, T(), receiver, it)
	finally:
		c.close()
	if result:
		conn.commit()
		return result
	log.debug('duplicate engage %s %s', receiver, it)


def url2tag(user_ID, url_):
	url = normalize_url(url_)
	if not url:
		log.debug('Bad URL %r' % (url_,))
		abort(400, 'Bad URL')

	c, tag = conn.cursor(), tag_for('%s∴%s' % (user_ID, url))
	try:
		result = write_tag(c, T(), tag, user_ID, url)
	finally:
		c.close()

	if result:
		conn.commit()
		log.debug('Tagged %s %r', tag, url)
	else:
		log.debug('Already tagged %s %r', tag, url)

	return bool(result), tag


def get_share(tag):
	c = conn.cursor()
	try:
		result = get_tag(c, tag)
	finally:
		c.close()
	if result:
		user_ID, url = result
		log.debug('Found %s %s %r', tag, user_ID, url)
		return user_ID, url
	log.debug('Missed %s', tag)
	abort(400, 'Unknown tag: %s' % tag)

def tag2url(tag):
	c = conn.cursor()
	try:
		url = get_tag(c, tag)
	finally:
		c.close()
	if url:
		log.debug('Found %s %r', tag, url)
		return url
	log.debug('Missed %s', tag)
	abort(400, 'Unknown tag: %s' % tag)


def normalize_url(url):
	try:
		result = urlparse(url)
	except:
		log.exception('While parsing URL %r', url)
		return
	if (result.scheme.lower() in ('http', 'https')
			and not (result.params or result.query or result.fragment)):
		return result.geturl()


def get_user_profile(user_ID):
	c = conn.cursor()
	try:
		profile_data = get_user_profile_db(c, user_ID)
	finally:
		c.close()
	if profile_data is None:
		abort(400, 'Unknown user: %r' % (user_ID,))
	return {
		'profile': profile_data
	}


def put_user_profile(user_ID, profile):
	c = conn.cursor()
	try:
		put_user_profile_db(c, user_ID, profile)
	finally:
		c.close()
		conn.commit()
