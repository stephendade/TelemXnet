#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for Devicedict
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
import random
import os

# via pip

# in this repo
from TelemXnet import devicedict


class DevicedatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.diccy = devicedict.Devicedict()

    def test_adddevice(self):
        device_id = random.randint(-64, 64)
        network_id = os.urandom(32)
        self.diccy.addremote(network_id, device_id, "127.0.0.1", 16250)

        (ip, port) = self.diccy.getremote(network_id, device_id)
        self.assertEqual((ip, port), ("127.0.0.1", 16250), "Can't get IP:port")

    def test_nodevice(self):
        device_id = random.randint(-64, 64)
        network_id = os.urandom(32)
        network_id_no = os.urandom(32)
        self.diccy.addremote(network_id, device_id, "127.0.0.1", 16250)

        (ip, port) = self.diccy.getremote(network_id, network_id_no)
        self.assertEqual((ip, port), (None, None), "Error with no device")
        
    def test_remotedevice(self):
        device_id = random.randint(-64, 64)
        network_id = os.urandom(32)
        self.diccy.addremote(network_id, device_id, "127.0.0.1", 16250)
        self.diccy.removeremote(network_id, device_id)

        (ip, port) = self.diccy.getremote(network_id, device_id)
        self.assertEqual((ip, port), (None, None), "Delete errored")

if __name__ == '__main__':
    unittest.main()
