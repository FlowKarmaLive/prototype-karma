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
from os.path import abspath
from pathlib import Path
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
    store_newkey_req,
    get_newkey_req,
    UnknownUserError,
    )
from bottle import Bottle, get, post, request, run, static_file, redirect, abort
from newkey import genkey


log = logging.getLogger('mon')

CLAVINGER = str(Path('./clavinger').resolve())
WEB = Path('../web').resolve()
STATIC_FILES = str(WEB / 'static')
TEMPLATES = WEB / 'templates'
INDEX_HTML = (TEMPLATES / 'index.html').read_text()
SHARE_HTML = (TEMPLATES / 'share.html').read_text()

app = Bottle()

@app.get('/')
def home_page():
    user_ID = get_user_ID()
    if not user_ID:
        redirect('/static/docs.html')
    return INDEX_HTML % dict(profile=json.dumps(get_user_profile(user_ID)))


def get_user_ID():
    '''
    Pull the user ID from the client cert "Client Subject".
    (We could also look up the cert serial no. in the DB and get the user
    ID from there.)
    '''
    sn = request.headers.get('X-Ssl-Client-Subject')
    if not sn:
        return
    return _parse_sn(sn)['CN']


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

    sender_profile = get_user_profile(sender_ID)

    server = request['HTTP_HOST']

    if bump(sender_ID, url_tag, user_ID):
        log.info('bump %s %s %s', sender_ID, user_ID, url_tag)

    share = share2tag(user_ID, url_tag)

    return SHARE_HTML % {
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

    tag = share.lstrip('∋')
    url = tag2url(tag)

    if engage(user_ID, tag):
        log.info('engage %s %s', user_ID, tag)

    redirect(url) # TODO: append the user_ID as a query arg?


@app.post('/newkey')
def newkey():
    '''
    This used to generate the cert, now it generates an URL to generate a cert.
    '''
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        abort(401, 'Unauthorized')

    user_ID = get_user_ID()
    if not user_ID:
        abort(401, 'Unauthorized')

    try:
        invite_no = get_and_increment_invite_count(user_ID)
    except UnknownUserError:
        abort(401, 'Unauthorized')

    new_user_ID = (
        ('%s-%s' % (user_ID, invite_no))
        if user_ID != '0'
        else str(invite_no)
        )

    code = store_newkey_req(new_user_ID, client_cert_serial_number)
    if not code:
        abort(500, '>_<')

    return "https://pub.flowkarma.live/join/%s" % (code,)


@app.get(r'/join/<new_user_ID:re:\d+(-\d+)*>')  # N{-N}
def join(new_user_ID):
    client_cert_serial_number = get_newkey_req(new_user_ID)
    if not client_cert_serial_number:
        abort(404, 'Huh?')
    parent, sep, _ = new_user_ID.rpartition('-')
    user_ID = parent if sep else '0'
    pw, filename = genkey(client_cert_serial_number, user_ID, new_user_ID)
    if not filename:
        abort(500, 'Idunnosomedamnthing.')
    return '''\
<!DOCTYPE HTML>
<html>
<body>
password: %s <br>
<a href="https://pub.flowkarma.live/vrty/%s" download>Download</a>
</body>
</html>''' % (pw, filename)

##    return static_file(filename, root=CLAVINGER, download=filename)


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
