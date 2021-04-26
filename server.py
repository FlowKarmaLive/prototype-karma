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
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        return static_file('unknown_index.html', root=TEMPLATES)
    sn = request.headers.get('X-Ssl-Client-Subject')
    sn = _parse_sn(sn)
    print(repr(sn))
    user_ID = sn['OU']  # for now, should be CN
    # user_ID = sn['CN']
    data = get_user_profile(user_ID)
    data['profile'] = json.dumps(data['profile'])

    INDEX_HTML = open(join(TEMPLATES, 'index.html'), 'r').read()
    # Reading the file per-request to not have to restart the server
    # to see changes to the template file.  Later this line above should
    # go back to module scope.

    return INDEX_HTML % data


def _parse_sn(sn):
    '''
    "/C=US/ST=CA/L=San Francisco/O=FlowKarma.Live/OU=${FROM}/CN=${NAME}"
    gets to the server as (e.g.)
    "CN=0-1,OU=0,O=FlowKarma.Live,L=San Francisco,ST=CA,C=US"
    '''
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
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        return static_file('unknown_index.html', root=TEMPLATES)

    url = request.params['url']  # Value 'request.params' is unsubscriptable ?  Linter error.
    unseen, tag = url2tag(user_ID, url)
    if unseen:
        log.info('register %s %s %r', user_ID, tag, url)

    server = request['HTTP_HOST']
    # TODO: check this value for hijinks.
    return "https://%s/∴%s" % (server, tag)


@app.get('/<share:re:∴[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def bump_anon_handler(share):
    '''Present the "Shared with you..." page.'''
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        redirect('/')
    tag = share[1:]
    sender, subject = get_share(tag)
    profile = get_user_profile(sender)['profile']
    server = request['HTTP_HOST']
    if bump(sender, subject, user_ID):
        log.info('bump %s %s %s', sender, subject, user_ID)
    unseen, mytag = url2tag(user_ID, subject)
    if unseen:
        log.info('register %s %s %r', user_ID, tag, subject)
    return open(join(TEMPLATES, 'share.html'), 'r').read() % {
        'from_profile': profile,
        'from_id': sender,
        'subject': json.dumps(subject),
        'bump_url':  "https://%s/∋%s" % (server, tag),
        'share_url': "https://%s/∴%s" % (server, mytag),
        }


@app.get('/<share:re:∋[23479cdfghjkmnp-tv-z]+>')  # tagly._chars
def eeee(share):
    '''Record a engage event.'''
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        redirect('/')
    tag = share[1:]
    _, subject = get_share(tag)
    if engage(user_ID, subject):
        log.info('engage %s %s', user_ID, subject)
    redirect(subject)


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

# C:\Users\sforman\Desktop\src\FKL\prototype-karma\clavinger\you.pfx
# C:\Users\sforman\Desktop\src\FKL\clavinger\you.pfx

@app.post('/profile')
def profile():
    '''Update user's profile.'''
    client_cert_serial_number = request.headers.get('X-Ssl-Client-Serial')
    if not client_cert_serial_number:
        abort(401, 'Unauthorized')
    sn = request.headers.get('X-Ssl-Client-Subject')
    sn = _parse_sn(sn)
    user_ID = sn['OU']  # for now, should be CN
    # user_ID = sn['CN']
    prof = request.body.read().decode('UTF_8')
    if len(prof) > 2048:
        abort(400, 'Profile too long.')
    put_user_profile(user_ID, prof)
    return ""

