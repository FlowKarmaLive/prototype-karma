#!/usr/bin/env python
import logging
from subprocess import run
from sys import platform
from tempfile import TemporaryDirectory
from pathlib import Path
from uuid import uuid4

from kpw import gen_passphrase
from stores import note_cert


log = logging.getLogger('mon.newkey')
command = 'sh -x newkey.sh'
KEYS_PATH = Path('./clavinger').absolute()


def genkey(newuid, parent_serial, nc=True):
    serial = uuid4().hex
    pw = gen_passphrase()
    fn = newuid + '.pfx'
    log.debug('Create new cert: %s %s', fn, serial)
    with TemporaryDirectory() as tmpdirname:
        completed_proc = run(
            command,
            capture_output=True,
            cwd=str(KEYS_PATH),
            env=dict(
                NAME=newuid,
                SERIAL='0x' + serial,
                TMPDIR=tmpdirname,
                KEYDIR=KEYS_PATH,
                PW=pw,
            ),
            shell=True,
        )
        if completed_proc.returncode:
            log.error('newkey script failure: %r', completed_proc.stderr)
            return
    log.debug('Created cert: %s %s', fn, serial)
    if nc:
        note_cert(serial, parent_serial, newuid)
    return pw, fn


if __name__ == '__main__':
    # Create "root" cert.
    print(*genkey('0', '0', '0', False))
