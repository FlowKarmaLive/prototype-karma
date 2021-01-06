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
import logging
from os.path import abspath
from stores import url2tag, tag2url, bump, engage, get_user_profile
from bottle import Bottle, get, post, request, run, static_file


log = logging.getLogger('mon')

STATIC_FILES = abspath('web/static')
TEMPLATES = abspath('web/templates')
SECRET_KEY = b"not a secret"

app = Bottle()

@app.get('/')
def home_page():
    user_ID = request.headers.get('X-Ssl-Client-Serial')
    if user_ID is None:
        return static_file('unknown_index.html', root=TEMPLATES)
    data = get_user_profile(user_ID)
    print(data)
    # how put data in page?
    # how Elm in page read data?
    return static_file('index.html', root=TEMPLATES)


@app.get('/favicon.ico')
def favicon_ico():
    return static_file('favicon.ico', root=STATIC_FILES)


@app.get('/static/<filename:path>')
def get_static(filename):
    return static_file(filename, root=STATIC_FILES)


@app.post('/reg')
def register():
    '''
    Accept an URL and return its tag, enter a register record in the DB
    if this is the first time we've seen this URL.
    '''
    url = request.params['url']  # Value 'request.params' is unsubscriptable ?  Linter error.
    unseen, tag = url2tag(url)
    if unseen:
        log.info('register %s %r', tag, url)
    return tag


@app.get('/bump'
     '/<sender:re:[a-z0-9]+>'
     '/<it:re:[a-z0-9]+>')
def bump_anon_handler(sender, it):
    '''Record the connection between two nodes in re: a "meme" URL.'''
    data = dict(
        from_url=tag2url(sender),
        iframe_url=tag2url(it),
        me=sender,
        it=it,
        server=request['HTTP_HOST'],
        )
    return str(data)


@app.get('/bump'
     '/<sender:re:[a-z0-9]+>'
     '/<it:re:[a-z0-9]+>'
     '/<receiver:re:[a-z0-9]+>')
def bump_handler(sender, it, receiver):
    '''Record the connection between two nodes in re: a "meme" URL.'''
    data = dict(
        from_url=tag2url(sender),
        iframe_url=tag2url(it),
        your_url=tag2url(receiver),
        me=sender,
        it=it,
        you=receiver,
        server=request['HTTP_HOST'],
        )
    if bump(sender, it, receiver):
        log.info('bump %s %s %s', sender, it, receiver)
    return str(data)


@app.get('/engage'
     '/<receiver:re:[a-z0-9]+>'
     '/<it:re:[a-z0-9]+>')
def engage_handler(receiver, it):
    '''
    Record the "engagement" of a user with some meme.

    Eventually this will generate some sort of correlation code that we
    return to the calling page which then passes it to the meme URL as a
    parameter letting whoever's on the other know who to thank.
    '''
    tag2url(receiver) ; tag2url(it)  # crude validation
    key = engage(receiver, it)
    if key:
        log.info('engage key:%s %s %s', key, receiver, it)
    return 'engaged'
