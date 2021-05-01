# Prototype/Demo for [FlowKarma.Live](https://FlowKarma.Live)


TODO:
    [X] client cert serial no. is not user ID
    [ ] create user 0 client cert
    [X] get a simple Elm client up and running
        [X] can edit and update profile
    [ ] password for client certs?
    [ ] reload bottle on file change?
    [X] proper table for sender-subject
    [ ] filter domains
    [ ] cert revocation

questions:
    Should we store user profiles at all?
    Should we request and store email addresses for users?
    Should we store and forward information between users?


=========================================================================
THIS README IS OUT OF DATE.

The whole point of the network is to publicly record the *provenance* of
ideas or memes, the graph of who-told-whom.  You're expected to have a
fairly stable set of direct contacts (12~25).  The network overall should
be a non-directed acyclic graph.

The first function of the server is just to provide a stable a mapping
from identifier URLs to opaque tags.

For users, the URLs serve to identify a user, (possibly by requiring the
URL to specify a resource that, when requested, contains the tag or some
other identity token.)  For now anyone can register any URL and get the
tag for it.  (In my ideal world, we make a IRL connection with the person
and install per-user certs in their browsers on each device they are
gonna wanna use with the network.)

The second function of the server is to log the origination, propagation,
and engagement with "memes" (in general, not just the funny captioned
images) represented as URLs.

This data is *public*.  It's published in blocks over bittorrent, with
the blocks lightly compressed such that you have to have the whole thing
to decode any part of it.  This means that everyone who wants to read and
use the data has to participate in swarm-serving the entire block.  It
also saves on bandwidth.

One wrinkle at the moment is that sites that won't display in an iframe
can't be transmitted using the server.  But that might be fun?


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
    - when you do it sets an `own_tag` cookie with your hash.
3. Then it redirects to a non-anon "bump URL" that
    - records the interaction
    - serves a page with the subject site in an iframe.
4. The header of the page offers you to
    - Forward the page to your contacts with new bump URLs.
    - Reject, with optional feedback.
    - Engage. (Redirect to the subject site.)


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

If a user who has an `own_tag` cookie set follows an anon bump from that
browser their tag will automatically be added to the end to make a proper
bump URL.


## Bump URLs

This API records the receipt of a message from one user to another, and
it returns a page that has the URL associated with that message open in
an iframe.

For a known member the bump URL contains all three tags, one for the
sender of the bump, one for the subject, and one for the receiver who has
made the request.

```
    http://localhost:8000/bump/<sender>/<subject>/<receiver>
```

The new network linkage between sender and receiver is logged.
The header above the iframe provides a context that allows for forwarding
rewritten bumps to that user's contacts.

If an unknown user (browser without an `own_tag` cookie) opens a bump URL
we treat is as an anon bump.


## Registering URLs to get tags (hashes)

At [http://localhost:8000/register](http://localhost:8000/register)
you'll see "Register an URL" and a single form field for entering an URL.
If you put an URL in there and click the button, a new panel will appear
with a "tag" for that URL (it's MD5 encoded in base 36) which can then be
used to make "bump" URLs.

Registering an URL doesn't set the `own_url` cookie.  You would typically
have done that when you first received an "anon bump".

## Misc URLs

This is a "scratchpad" for bump URLs and whatnot.

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





------------------------------------------


A lot of the above is changed slightly or a lot.


## User IDs

For user IDs I think I'm going to use an open-ended text-based key that
encodes the lineage of a user.

The first user is user "0".  The first user you invite is N + "-1" where
N is your ID, the second is N + "-2" and so on.

So "4-7-1-3" is the user ID of the third person invited by the first
person invited by the seventh person invited by the fourth member.

Got it?

Then the serial # or tag is just derived from that, because why not?

So I think for each user we want to keep the ID and also the number of
invites sent so far.



