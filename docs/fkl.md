FK.L is a
[provenance](https://en.wikipedia.org/wiki/Provenance)
network.  By participating you help create a public
graph of the spread of an idea (represented by an URL/website).

## Joining the FlowKarma.Live Network

FK.L doesn't use passwords.  Instead we rely on
[client certificates](https://en.wikipedia.org/wiki/Client_certificate)
that you install in your browser.  These "cert" files act as unforgeable
keys that identify your web browser to our web servers automatically.

1. Your friend gives you a \*.pfx certificate file.
2. Install the cert file into your web browser(s).
3. Visit <https://flowkarma.live/> and when your browser asks which
   cert file to use select the one you just installed.
4. Set your profile.

Now you are ready to use [FlowKarma.Live](https://flowkarma.live/).

## Home Page

When you visit [FlowKarma.Live](https://flowkarma.live/) with a browser
that has your cert file installed you'll see three sections:

### About You

This is where you can update your user profile.

### Share an URL

This is where you enter *new* subject URLs to get "bump" URLs to share.

### Invite New Members

This button will create and download a new cert file for a new user.
Give it to your friend and then delete your copy.  (Cert files are
deleted from the server after a few minutes and cannot be recovered or
recreated.  If you need a new cert for an existing user for some reason
you should contact us on the
[mailing list](https://lists.sr.ht/~sforman/fkl-users)
for manual intervention.)


## Bump URLs

Someone sends you a "bump" URL that starts with "∴" followed by a code or
tag that identifies the sender and the subject URL.  E.g.:

- <https://flowkarma.live/∴t4o3328q0fdz4ov6dgeyfa>

When you visit such a link for the first time from a browser with your
cert file installed in it an entry is recorded in the public FK.L
database documenting the connection.  This is how the per-subject
connection graph grows.

You then are presented with a page that has the following sections:

### From

This displays the user profile of the sender.

### Sharing

There is a direct link to the subject URL so you can click through and
"preview" the content (without *engaging* with it) and an *Engage* button
that will record an "engage" event between your user ID and the subject
URL in the public FK.L database and then redirect you to the URL.

### Share

There is a new "bump" URL that identifies *you* as the sender for the
subject URL.  This is the URL to share with your contacts to expand the
link graph.

------------------------

## User IDs

User IDs are automatically assigned and can't be changed.  They consist
of numbers separated by dashes, and the encode the "lineage" of user
membership.  It's easier to give an example than to explain.  The user ID
"4-7-3-5" is the fifth member invited by the third member invited by the
seventh member invited by the fourth member to join (from direct invites
at the "dawn time" of the network.)

Each of the people invited by user "4-7-3-5" will get the user IDs:
"4-7-3-5-1", "4-7-3-5-2", "4-7-3-5-3" and so on "4-7-3-5-...".


## User Profiles

User profiles are a brief (~2000 Unicode characters) piece of text that
should identify you to your contacts.  This information is public to all
members.

It is suggested that the kind of information you might want to include in
your profile could be:

- Your name or handle
- Methods to communicate with you:
  - Email
  - Twitter or other social networks
  - etc...
- Links to your blog/site/project/etc...
- A bit about yourself and your motivation(s) for participating in FK.L


## Road Map

1. Experimental Stage
2. Form a Business Structure
3. Long-term Maintenance Mode


## Philosophy of Business

1. Member-owned
2. Transparent Governance
3. Open Books (as per "Honest Business" by Phillips & Rasberry)


## Contact Us

The best way to communicate with me about FK.L is on the public mailing
list:
[fkl-users Mailing List](https://lists.sr.ht/~sforman/fkl-users)


