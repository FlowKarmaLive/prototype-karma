#!/usr/bin/env python
from sys import platform
from subprocess import run

if platform == 'win32':
    command = [r"C:\Program Files\Git\git-bash.exe", 'newkey.sh']
else:
    command = 'sh newkey.sh'

def genkey(parent, child, serial):
    return run(
        command,
        shell=True,
        env=dict(
            FROM=parent,
            NAME=child,
            SERIAL=serial,
        ),
        capture_output=True,
        cwd=r'./clavinger',
    )

if __name__ == '__main__':
    p = genkey('cats', 'rats', '0')
