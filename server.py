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
from os.path import abspath, join
from stores import (
    bump,
    engage,
    get_and_increment_invite_count,
    get_share,
    get_user_profile,
    put_user_profile,
    tag2url,
    url2tag,
    share2tag,
    tag2share,
    )
from bottle import Bottle, get, post, request, run, static_file, redirect, abort
from newkey import genkey


log = logging.getLogger('mon')

STATIC_FILES = abspath('web/static')
TEMPLATES = abspath('web/templates')
SECRET_KEY = b"not a secret"

app = Bottle()

@app.get('/')
def home_page():
    user_ID = get_user_ID()
    if not user_ID:
        return static_file('unknown_index.html', root=TEMPLATES)

    data = get_user_profile(user_ID)
    data['profile'] = json.dumps(data['profile'])

    INDEX_HTML = open(join(TEMPLATES, 'index.html'), 'r').read()
    # Reading the file per-request to not have to restart the server
    # to see changes to the template file.  Later this line above should
    # go back to module scope.

    return INDEX_HTML % data


def get_user_ID():
    sn = request.headers.get('X-Ssl-Client-Subject')
    if not sn:
        return
    return _parse_sn(sn)['OU']  # for now, should be CN


def _parse_sn(sn):
    '''
    "/C=US/ST=CA/L=San Francisco/O=FlowKarma.Live/OU=${FROM}/CN=${NAME}"
    gets to the server as (e.g.)
    "CN=0-1,OU=0,O=FlowKarma.Live,L=San Francisco,ST=CA,C=US"
    '''
    # TODO: get just the parts we want, a whole dict is a bit much.
    return dict(t.split('=') for t in sn.split(',') if '=' in t)


@app.get('/favicon.ico')
def favicon_ico():
    return static_file('favicon.ico', root=STATIC_FILES)


# Uncomment this route & handler to support dev (in other words, if caddy
# is not there to serve them for us.)

# @app.get('/static/<filename:path>')
# def get_static(filename):
#     return static_file(filename, root=STATIC_FILES)


@app.post('/reg')
def register():
    '''
    Accept an URL and return its tag, enter a register record in the DB
    if this is the first time we've seen this URL.
    '''
    user_ID = get_user_ID()
    if not user_ID:
        abort(401, 'Unauthorized')

    url = request.params['url']  # Value 'request.params' is unsubscriptable ?  Linter error.
    unseen, tag = url2tag(url)
    if unseen:
        log.info('register %s %s %r', user_ID, tag, url)

    share = share2tag(user_ID, tag)

    server = request['HTTP_HOST']
    # TODO: check this value for hijinks.

    return "https://%s/∴%s" % (server, share)


@app.get('/<tag:re:∴[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def share_handler(tag):
    '''Present the "Shared with you..." page.'''
    user_ID = get_user_ID()
    if not user_ID:
        # TODO redirect to a page with some helpful info or something.
        redirect('/')

    sender_ID, url_tag = tag2share(tag.lstrip('∴'))
    url = tag2url(url_tag)

    sender_profile = get_user_profile(sender_ID)['profile']

    server = request['HTTP_HOST']

    if bump(sender_ID, url_tag, user_ID):
        log.info('bump %s %s %s', sender_ID, user_ID, url_tag)

    share = share2tag(user_ID, url_tag)

    return open(join(TEMPLATES, 'share.html'), 'r').read() % {
        'from_profile': sender_profile,
        'from_id': sender_ID,
        'subject': json.dumps(url),
        'bump_url':  "https://%s/∋%s" % (server, url_tag),
        'share_url': "https://%s/∴%s" % (server, share),
        }


@app.get('/<share:re:∋[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def engage_handler(share):
    '''Record a engage event.'''
    user_ID = get_user_ID()
    if not user_ID:
        redirect('/')

    url = tag2url(share.lstrip('∋'))

    if engage(user_ID, url):
        log.info('engage %s %s', user_ID, url)

    redirect(url) # TODO: append the user_ID as a query arg?


@app.get('/newkey')
def newkey():
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        abort(401, 'Unauthorized')
    # sn = request.headers.get('X-Ssl-Client-Subject')
    # CN=rats,OU=cats,O=FlowKarma.Live,L=San Francisco,ST=CA,C=US
    invite_no = get_and_increment_invite_count(user_ID)
    new_user_ID = str(int(user_ID) * 100000 + invite_no)
    print(user_ID, new_user_ID)
    genkey(user_ID, new_user_ID, new_user_ID)
    filename = new_user_ID + '.pfx'
    return static_file(filename, root=abspath('clavinger'), download=filename)


@app.post('/profile')
def profile():
    '''Update user's profile.'''
    user_ID = get_user_ID()
    if not user_ID:
        abort(401, 'Unauthorized')

    # TODO: log the update somewhere?  In the db?
    # client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')

    prof = request.body.read().decode('UTF_8')
    # TODO: detect and handle encoding errors.

    if len(prof) > 2048:
        abort(400, 'Profile too long.')

    put_user_profile(user_ID, prof)
    return ""
