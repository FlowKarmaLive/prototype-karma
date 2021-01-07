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
'''
Tags are lowercase ASCII letters and digits with potentially ambiguous
characters and vowels removed.  This leaves these twenty-four characters:

    2 3 4 7 9 c d f g h j k m n p q r s t v w x y z

First we find the MD5 sum of the URL, take the integer that that
represents as a hexidecimal number, and then encode that in base-24 with
the above symbols, in reverse order, as numerals.
'''
from hashlib import md5


_chars = '23479cdfghjkmnpqrstvwxyz'
_base = len(_chars)
_char = _chars.__getitem__


def to_base(i):
	return ''.join(_to_base(i))


def _to_base(i):
	while i:
		i, r = divmod(i, _base)
		yield _char(r)


def tag_for(s):
	return to_base(int(md5(s.encode('utf_8')).hexdigest(), 16))


if __name__ == '__main__':
	m = md5(b"Hey! Funny").hexdigest()
	n = int(m, 16)
	M = to_base(n)
	print('hash   ', m)
	print('int    ', n)
	print('base', _base, M)
