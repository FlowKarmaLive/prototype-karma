# -*- coding: utf-8 -*-
#
#	Copyright © 2016, 2020, 2021 Simon Forman
#
#	This file is part of FlowKarma.Live.
#
#	FlowKarma.Live is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	FlowKarma.Live is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with FlowKarma.Live.	 If not, see <http://www.gnu.org/licenses/>.
#
import logging


F = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')


def setup_log(extra_record=False):
	log = logging.getLogger('mon')
	log.setLevel(logging.DEBUG)

	# sh = logging.StreamHandler()
	# sh.setLevel(logging.INFO)
	# sh.setFormatter(F)
	# log.addHandler(sh)

	fh = logging.FileHandler('memestreamer.log')
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(F)
	log.addHandler(fh)

	if extra_record:
		fh = logging.FileHandler('record.log')
		fh.setLevel(logging.INFO)
		fh.setFormatter(logging.Formatter('%(created)f %(message)s'))
		log.addHandler(fh)

	return log

