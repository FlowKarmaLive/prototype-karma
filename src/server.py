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
from email.utils import formatdate
from os.path import abspath
from pathlib import Path
from time import time
from urllib.parse import quote, urlparse

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
    get_old_newkey_req,
    UnknownUserError,
    )
from bottle import (
    Bottle,
    get,
    post,
    request,
    run,
    static_file,
    redirect,
    abort,
    HTTPResponse,
    )
from newkey import genkey


log = logging.getLogger('mon')


_CLAVINGER = Path('./clavinger').resolve()
CLAVINGER = str(_CLAVINGER)
WEB = Path('../web').resolve()
STATIC_FILES = str(WEB / 'static')
TEMPLATES = WEB / 'templates'
INDEX_HTML = (TEMPLATES / 'index.html').read_text()
SHARE_HTML = (TEMPLATES / 'share.html').read_text()
NEWKEY_HTML = (TEMPLATES / 'newkey.html').read_text()
UNAUTH_HOME = 'https://pub.flowkarma.live/doc/'


app = Bottle()


@app.get('/')
def home_page():
    user_ID = get_user_ID()
    if not user_ID:
        redirect(UNAUTH_HOME)
    return INDEX_HTML % dict(profile=json.dumps(get_user_profile(user_ID)))


def get_user_ID():
    '''
    Pull the user ID from the client cert "Client Subject".
    (We could also look up the cert serial no. in the DB and get the user
    ID from there.)
    '''
    sn = request.headers.get('X-Ssl-Client-Subject')
    if sn:
        i = sn.find('CN=')
        if i >= 0:
            i += 3
            j = sn.find(',', i)
            return sn[i:j] if j >= 0 else sn[i:]


# Uncomment thse to serve static content in e.g. dev.
# (In other words, if caddy is not there to serve them for us.)

# @app.get('/favicon.ico')
# def favicon_ico():
#     return static_file('favicon.ico', root=STATIC_FILES)

# @app.get('/static/<filename:path>')
# def get_static(filename):
#     return static_file(filename, root=STATIC_FILES)


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


def normalize_url(url):
    try:
        result = urlparse(url)
    except:
        log.exception('While parsing URL %r', url)
        return
    if result.scheme.lower() in ('http', 'https'):
        return quote(result.geturl())


@app.post('/reg')
def register():
    '''
    Accept an URL and return its tag, enter a register record in the DB
    if this is the first time we've seen this URL.
    '''
    user_ID = get_user_ID()
    if not user_ID:
        abort(401, 'Unauthorized')

    url_ = request.params['url']  # Value 'request.params' is unsubscriptable ?  Linter error.
    url = normalize_url(url_)
    if not url:
        abort(400, 'Bad URL')

    unseen, tag = url2tag(url)
    if unseen:
        log.info('register %s %s %s', user_ID, tag, url)

    return "https://flowkarma.live/∴" + share2tag(user_ID, tag)


@app.get('/<tag:re:∴[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def share_handler(tag):
    '''Present the "Shared with you..." page.'''
    user_ID = get_user_ID()
    if not user_ID:
        redirect(UNAUTH_HOME)

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
        redirect(UNAUTH_HOME)

    tag = share.lstrip('∋')
    url = tag2url(tag)

    if engage(user_ID, tag):
        log.info('engage %s %s', user_ID, tag)

    redirect(url) # TODO: append the user_ID as a query arg?


@app.post('/newkey')
def newkey():
    '''
    Generate an URL to generate a cert.
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


@app.get(r'/join/<code:re:[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def join(code):
    result = get_newkey_req(code)
    if not result:
        abort(404, 'join code %s invalid or expired' % (code,))
    pw, filename = genkey(*result)
    if not filename:
        abort(500, 'Idunnosomedamnthing.')
    return NEWKEY_HTML % dict(pw=pw, code=code)


@app.get(r'/vrty/<code:re:[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def vrty(code):
    result = get_old_newkey_req(code)
    if not result:
        abort(404, 'join code %s invalid or expired' % (code,))
    new_user_ID, _ = result
    fn = new_user_ID + '.pfx'
    f = _CLAVINGER / fn
    if not f.exists():
        abort(404, '%r not found' % (fn,))
    stats = f.stat()
    headers = {
        'Content-Type': 'application/x-pkcs12; charset=UTF-8',
        'Content-Disposition': 'attachment; filename="%s"' % (fn,),
        'Content-Length': stats.st_size,
        'Last-Modified': formatdate(stats.st_mtime, usegmt=True),
        'Date': formatdate(time(), usegmt=True),
        }
    body = f.read_bytes()
    f.unlink()
    return HTTPResponse(body, **headers)
