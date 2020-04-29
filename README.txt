Registration
================================

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



