#!/usr/bin/env python
import logging
from shutil import move
from subprocess import run
from sys import platform
from tempfile import TemporaryDirectory
from pathlib import Path
from uuid import uuid4

from stores import note_cert


log = logging.getLogger('mon.newkey')
command = 'sh -x newkey.sh'
KEYS_PATH = Path('./clavinger').absolute()


def genkey(client_cert_serial_number, parent, child):
    serial = uuid4().hex
    fn = child + '.pfx'
    log.debug('Create new cert: %s %s', fn, serial)
    keyfn = KEYS_PATH / fn
    with TemporaryDirectory() as tmpdirname:
        completed_proc = run(
            command,
            capture_output=True,
            cwd=str(KEYS_PATH),
            env=dict(
                FROM=parent,
                NAME=child,
                SERIAL='0x' + serial,
                TMPDIR=tmpdirname,
            ),
            shell=True,
        )
        if completed_proc.returncode:
            log.error('newkey script failure: %r', completed_proc.stderr)
            return
        log.debug('Created cert: %s %s', fn, serial)
        move(str(Path(tmpdirname) / fn), str(keyfn))
        # Can't rename, tmp is on a diff fs leading to
        # "OSError: [Errno 18] Cross-device link"
        # on digitalocean.

    note_cert(serial, parent, client_cert_serial_number, child)
    return fn


if __name__ == '__main__':
    # Create "root" cert.
    p = genkey('0', '0', '0')
