#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for unipacket
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
from TelemXnet import unipacket


class UnipacketTestCase(unittest.TestCase):
    def setUp(self):
        self.device_id = random.randint(-64, 64)
        self.network_id = os.urandom(32)
        self.sequence = random.randint(0, 1000000)
        self.payload = os.urandom(16)

        self.pkt = unipacket.Unipacket()
        self.msg = self.pkt.buildpacket(self.network_id, self.device_id,
                                        self.sequence, self.payload)
        self.ret_pkt = self.pkt.recoverpacket(self.msg)

    def test_packet(self):
        self.assertNotEqual(self.msg, None, "Encoded Packet is None")

    def test_header(self):
        self.assertEqual(self.msg[0], 0, "Incorrect packet header")

    def test_networkid(self):
        self.assertEqual(self.network_id, self.ret_pkt.NetworkID,
                         "Incorrect NetworkID")

    def test_deviceid(self):
        self.assertEqual(self.device_id, self.ret_pkt.DeviceID,
                         "Incorrect DeviceID")

    def test_sequence(self):
        self.assertEqual(self.sequence, self.ret_pkt.Sequence,
                         "Incorrect Timestamp")

    def test_payload(self):
        self.assertEqual(self.payload, self.ret_pkt.Payload,
                         "Incorrect Payload")

    def test_corruptpacket(self):
        bad_msg = self.msg
        bad_msg = bad_msg[:3] + b"+" + bad_msg[3+1:]
        self.assertEqual(self.pkt.recoverpacket(bad_msg), None, "Bad CRC")

    def test_badpacket(self):
        bad_msg = self.msg
        bad_msg = bad_msg[3:]
        self.assertEqual(self.pkt.recoverpacket(bad_msg), None, "Bad Packet")

    def test_baddeviceid(self):
        bad_device_id = 68
        msg = self.pkt.buildpacket(self.network_id, bad_device_id,
                                   self.sequence, self.payload)
        self.assertEqual(msg, None, "Bad DeviceID")

    def test_badnetworkid(self):
        bad_network_id = 'q77c89340cq49'
        msg = self.pkt.buildpacket(bad_network_id, self.device_id,
                                   self.sequence, self.payload)
        self.assertEqual(msg, None, "Bad NetworkID")

    def test_badsequence(self):
        bad_sequence = "dfg"
        msg = self.pkt.buildpacket(self.network_id, self.device_id,
                                   bad_sequence, self.payload)
        self.assertEqual(msg, None, "Bad Sequence")

    def test_badpayload(self):
        bad_payload = ""
        msg = self.pkt.buildpacket(self.network_id, self.device_id,
                                   self.sequence, bad_payload)
        self.assertEqual(msg, None, "Bad Payload")

if __name__ == '__main__':
    unittest.main()
