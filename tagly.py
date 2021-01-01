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
from hashlib import md5
from string import digits


STR = (digits + 'abcdefghijklmnopqrstuvwxyz').__getitem__


def to36(i):
	acc = []
	while i:
		i, r = divmod(i, 36)
		acc.append(STR(r))
	return ''.join(acc[::-1])


def tag_for(s):
	return to36(int(md5(s.encode('utf_8')).hexdigest(), 16))


if __name__ == '__main__':
	m = md5(b"Hey! Funny").hexdigest()
	n = int(m, 16)
	print(n, m)
	M = to36(n)
	print(int(M, 36), M)
