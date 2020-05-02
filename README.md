# Prototype/Demo for [FlowKarma.Live](https://FlowKarma.Live)


Lorem...

## Install

Clone the repo.  Make sure you have the deps installed (TODO: setup.py,
or pyproject.toml, or whatever): `sqlite3`   ...I think that's it.

Make sure you have Python 3, change into the repo dir and:

```
    $ python run.py 
    Bottle v0.13-dev server starting up (using WSGIRefServer())...
    Listening on http://localhost:8000/
    Hit Ctrl-C to quit.
```

There you go.  The root path is 404 at the moment.  Start at
[http://localhost:8000/register](http://localhost:8000/register)


## Walkthrough

In normal operation:

1. You hear about FK.L from a friend and they send you an "anon bump
   URL".
2. You follow that URL,
    - the system prompts you to select a site/URL to represent yourself
    - sets an `own_tag` cookie with the hash.
3. Then it redirects to a non-anon "bump URL" that
    - records the interaction
    - serves a page with the subject site in an iframe.
4. The header of the page offers you to
    - Forward the page to your contacts with new bump URLs.
    - Reject, with optional feedback.
    - Engage. (Redirect to the subject site.)



## Registration

At that URL 
[http://localhost:8000/register](http://localhost:8000/register)
you'll see "Register an URL" and a single form field for entering an URL.
If you put an URL in there and click the button, a new panel will appear
with a "tag" for that URL (it's MD5 encoded in base 36) which can then be
used to make "bump" URLs.

Registering an URL doesn't set the `own_url` cookie.  You would typically
have done that when you first received an "anon bump".

## Anonymous Bumps

This is an URL sent to you by a friend that has only two hashes in it:
the sender's and the subject's.
[Register](http://localhost:8000/register) a few URLS, e.g.:

```
85r32bnav3tj6jmvfwj1wfyxu http://localhost:8000/register
1yjzqv59md3ndkouycwl7yrj0 https://en.wikipedia.org/wiki/SQLite
eus303iri9v7oxm2u2dl8dqfi https://sqlite.org/cli.html
c81aaxp0mf8hn95o3bawr6ftt https://bottlepy.org/docs/dev/routing.html
74bteivzc9y7tbqlq81z99pu1 https://www.dillo.org/
dbot4o3328q0fdz4ov6dgeyfa https://www.sqlalchemy.org/
```

Then construct an url like this:

```
http://localhost:8000/bump/<sender>/<subject>
```

So if we imagine that Dillo wants to tell you about Sqlalchemy the *anon
bump URL* would look like this:

```
http://localhost:8000/bump/74bteivzc9y7tbqlq81z99pu1/dbot4o3328q0fdz4ov6dgeyfa
```


## Bump URLs

--------------------

Before I go on I should go find the other stuff I've written so I'm not
repeating myself.

--------------------


Just a mapping from identifier URLs to opaque tags.

The URLs identify a user, possibly by requiring the URL to specify a
resource that, when requested, contains the tag or some other identity
token.  For now anyone can register any URL and get the tag for it.  (In
my ideal world, we make a IRL connection with the person and install
per-user certs in their browsers on each device they are gonna wanna use
with the network.  We'll see if that flies.)

The tags are kept in a database and used to lookup URLs.


Bump
================================

This API records the receipt by a user (known or new) of a message from a
user and returns the URL associated with that message.  There are two
kinds of "bumps" differentiated by whether or not the receiver is already
known (has a tagged URL.)

For a known member the bump URL contains all three tags, one for the
sender of the bump, one for the subject, and one for the receiver who has
made the request.

    /bump/<sender>/<subject>/<receiver>/

The new network linkage between sender and receiver is logged and the URL
of the subject is returned to the receiver (along with a context or
supplement that allows for sending bumps to that user's contacts.  Client
behavior is not fully specified in this document.)

For unknown (new) users we return a page that lets them register their
own URL and continue.


Engage
================================


/bump/<sender>/<subject>/<receiver>/



http://localhost:8000/bump/2v1n9adqg9gdmijwc6bcl2gjt/2v1n9adqg9gdmijwc6bcl2gjt/2v1n9adqg9gdmijwc6bcl2gjt

http://localhost:8000/bump/c81aaxp0mf8hn95o3bawr6ftt/c81aaxp0mf8hn95o3bawr6ftt/c81aaxp0mf8hn95o3bawr6ftt

c81aaxp0mf8hn95o3bawr6ftt


http://localhost:8000/bump/7b7uylpbadz5zsm9r3uf7oy9y/74bteivzc9y7tbqlq81z99pu1

http://localhost:8000/bump/


c81aaxp0mf8hn95o3bawr6ftt/c81aaxp0mf8hn95o3bawr6ftt


http://localhost:8000/bump/2v1n9adqg9gdmijwc6bcl2gjt/2v1n9adqg9gdmijwc6bcl2gjt/2v1n9adqg9gdmijwc6bcl2gjt

ax1z1leauxbuaxgyn83uuesh6
239qr624jpvwusnyzj7wzj2oi
dourrlegdsk0q1ddcen9l2wuj

http://localhost:8000/bump/dourrlegdsk0q1ddcen9l2wuj/239qr624jpvwusnyzj7wzj2oi



http://localhost:8000/bump/5hc6mj8chr78r6tghd5m3dgxz/239qr624jpvwusnyzj7wzj2oi/
http://localhost:8000/bump/5hc6mj8chr78r6tghd5m3dgxz/239qr624jpvwusnyzj7wzj2oi/

