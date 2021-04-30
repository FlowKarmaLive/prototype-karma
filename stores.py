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
'''
This module handles the interface between Python code and the SQLite DB
file.

It's kind of a mess right now because it was in two modules (high-level
for generic code and low-level for DB-specific code) and I combined it
into one (because I like to go back and forth between atomized multi-file
arrangement and monolithic uni-module arrangement.  Dunno exactly why.)

There's a single module-level connection object that is initialized by
the main module at start-time.  (The DB is a file so if the connection
ever has a problem "reaching" it we have bigger problems than only having
one singleton conn.)

SQL code literals are scattered around;  I'm pretty sure I'm missing or
misusing the rollback() method;  the whole thing could use a good
cleaning.

'''
import logging, json
from urllib.parse import urlparse
import sqlite3
from bottle import abort
from tagly import tag_for
from time import time


log = logging.getLogger('mon.db')
conn = None


CREATE_TABLES = '''\
create table bumps (when_ INTEGER, key TEXT PRIMARY KEY, from_ TEXT, what TEXT, to_ TEXT)
create table tags (when_ INTEGER, tag TEXT PRIMARY KEY, url TEXT)
create table engages (when_ INTEGER, key TEXT PRIMARY KEY, who TEXT, what TEXT)
create table users (when_ INTEGER, key TEXT PRIMARY KEY, profile TEXT, invites INTEGER)
create table shares (when_ INTEGER, tag TEXT PRIMARY KEY, from_ TEXT, what TEXT)
create table certs (when_ INTEGER, serial_no TEXT PRIMARY KEY, parent_user TEXT, parent_cert_serial_no TEXT, user TEXT)
'''.splitlines(False)


SQL_0 = 'insert into bumps values (?, ?, ?, ?, ?)'
SQL_1 = 'insert into engages values (?, ?, ?, ?)'
SQL_2 = 'insert into tags values (?, ?, ?)'
SQL_3 = 'select profile from users where key=?'
SQL_4 = 'update users set profile=? where key=?'
SQL_5 = 'select url from tags where tag=?'
SQL_6 = 'select when_, from_, to_ FROM bumps WHERE what=?'
SQL_7 = 'insert into users values (?, ?, ?, ?)'
SQL_8 = 'insert into certs values (?, ?, ?, ?, ?)'
SQL_9 = 'insert into shares values (?, ?, ?, ?)'
SQL_10 = 'select from_, what FROM shares WHERE tag=?'


INITIAL_PROFILE = '''\
Welcome to FlowKarma.Live
Edit this text and click the "Update" button below to update your profile.
This will be public, use it to identify yourself and provide contact information.
'''


def note_cert(serial, parent, client_cert_serial_number, child):
    c = conn.cursor()
    try:
        c.execute(SQL_8, (T(), serial, parent, client_cert_serial_number, child))
    finally:
        c.close()
    conn.commit()


def get_and_increment_invite_count(user_ID):
    c = conn.cursor()
    try:
        c.execute('select invites from users where key=?', (user_ID,))
        result = c.fetchone()
    finally:
        c.close()
    if result is None:
        raise ValueError('???')
    n = result[0] + 1
    c = conn.cursor()
    try:
        c.execute('update users set invites=? where key=?', (n, user_ID))
    finally:
        c.close()
    conn.commit()
    return n


def connect(db_file=':memory:', create_tables=True):
    global conn
    if conn:
        raise RuntimeError('DB already connected %r', conn)
    conn = sqlite3.connect(db_file)
    conn.row_factory = VisibleRow
    if create_tables:
        c = conn.cursor()
        for statement in CREATE_TABLES:
            c.execute(statement)
        c.execute(  # Create User Zero.
            SQL_7,
            (T(), '0', 'Hello, and welcome to the middle of the app.', 0)
        )
        c.close()
        conn.commit()


class VisibleRow(sqlite3.Row):
    def __str__(self):
        return str(tuple(self))
    __repr__ = __str__


def bump(sender, it, receiver):
    key = tag_for('%s:%s' % (it, receiver))
    c = conn.cursor()
    try:
        result = insert(c, SQL_0, T(), key, sender, it, receiver)
    finally:
        c.close()
    if result:
        conn.commit()
        return True
    conn.rollback()
    log.debug('duplicate bump %s %s %s', sender, it, receiver)
    return False


def engage(receiver, it):
    key = tag_for('%s:%s' % (receiver, it))
    c = conn.cursor()
    try:
        result = insert(c, SQL_1, T(), key, receiver, it)
        result = None if result is None else key
    finally:
        c.close()
    if result:
        conn.commit()
        return result
    conn.rollback()
    log.debug('duplicate engage %s %s', receiver, it)


def share2tag(from_, what):
    c, tag = conn.cursor(), tag_for('%s∴%s' % (from_, what))
    try:
        result = insert(c, SQL_9, (T(), tag, from_, what))
    finally:
        c.close()
    if result:
        conn.commit()
    return tag


def tag2share(tag):
    c = conn.cursor()
    try:
        c.execute(SQL_10, (tag,))
        result = c.fetchone()
    finally:
        c.close()
    if not result:
        log.debug('Missed %s', tag)
        abort(400, 'Unknown tag: %s' % tag)
    return result


def url2tag(url_):
    '''
    Return (bool, tag) for an URL where the bool indicates
    whether we have this URL in the DB already.
    '''
    url = normalize_url(url_)
    if not url:
        log.debug('Bad URL %r' % (url_,))
        abort(400, 'Bad URL')

    c, tag = conn.cursor(), tag_for(url)
    try:
        result = insert(c, SQL_2, T(), tag, url)
    finally:
        c.close()

    if result:
        conn.commit()
        log.debug('Tagged %s %r', tag, url)
    else:
        conn.rollback()
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
        url = url[0]
        log.debug('Found %s %r', tag, url)
        return url
    log.debug('Missed %s', tag)
    abort(400, 'Unknown tag: %s' % tag)  # TODO remove this...


def normalize_url(url):
    try:
        result = urlparse(url)
    except:
        log.exception('While parsing URL %r', url)
        return
    if result.scheme.lower() in ('http', 'https'):
        return result.geturl()


def get_user_profile(user_ID):
    c = conn.cursor()
    try:
        c.execute(SQL_3, (user_ID,))
        result = c.fetchone()
    finally:
        c.close()
    if result:
        return {  # TODO this needn't be a dict.
            'profile': result[0]
        }
    # A new user?
    c = conn.cursor()
    try:
        c.execute(  # Create User record.
            SQL_7,
            (T(), user_ID, INITIAL_PROFILE, 0)
        )
    finally:
        c.close()
    return {'profile': INITIAL_PROFILE}

    # abort(400, 'Unknown user: %r' % (user_ID,))  # TODO also remove this...


def put_user_profile(user_ID, profile):
    c = conn.cursor()
    try:
        c.execute(
            SQL_4,
            (profile, user_ID)
            )
    except:
        conn.rollback()
    else:
        conn.commit()
    finally:
        c.close()
    # Is this okay?  Close cursor AFTER conn {commit,rollback}?


def insert(c, query, *values):
    try:
        c.execute(query, values)
    except sqlite3.IntegrityError:
        return
    return c.lastrowid


def T():
    return int(round(time(), 3) * 1000)


def get_tag(c, tag):
    c.execute(SQL_5, (tag,))
    return c.fetchone()


def extract_graph(c, tag):
    c.execute(SQL_6, (tag,))
    nodes, links = set(), []
    for when, from_, to in c.fetchall():
        nodes.update((from_, to))
        links.append((when, from_, to))
    return list(nodes), links
