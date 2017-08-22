#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for misc utilities
#
#  Copyright 2017 Stephen Dade <stephen_dade@hotmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

# Default python libs
import unittest
import time

# Via pip

# in this repo
from TelemXnet import util


class UtilTestCase(unittest.TestCase):
    def test_timestamp(self):
        tmstmp = util.gettimestamp()

        # assert that it makes sense
        self.assertTrue(tmstmp > 0, "timestamp less than 0")

        # check accuracy - 1ms accuracy required
        # do many times and check accuracy is less than 2.0ms
        for i in range(0, 100):
            tsOne = util.gettimestamp()
            time.sleep(0.001)
            tsTwo = util.gettimestamp()
            self.assertTrue((tsTwo - tsOne) < 20, "Time accuracy wrong")

if __name__ == '__main__':
    unittest.main()
