#!/usr/bin/env python
from subprocess import run


def newkey(parent, child, serial):
    env = dict(
        FROM=parent,
        NAME=child,
        SERIAL=serial,
    )
    return run(
        'sh newkey.sh',
        shell=True,
        env=env,
    )

if __name__ == '__main__':
    p = newkey('cats', 'rats', '123345546567')
