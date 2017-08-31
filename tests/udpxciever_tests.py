#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for Uxpxciever
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
import time
import unittest
import random
import os
import threading
import socket

# Via pip

# in this repo
from TelemXnet import unipacket
from TelemXnet import udpxciever


class UDPEchoServer(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.isExit = False

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        while not self.isExit:
            payload, client_address = sock.recvfrom(512)
            # print("Echoing data back to " + str(client_address))
            sock.sendto(payload, client_address)
        sock.close()

    def exit(self):
        self.isExit = True


class UnipacketTestCase(unittest.TestCase):
    def setUp(self):
        # make a packet
        self.device_id = random.randint(-64, 64)
        self.network_id = os.urandom(32)
        self.sequence = random.randint(0, 1000000)
        self.payload = os.urandom(16)

        self.pkt = unipacket.Unipacket()
        self.msg = self.pkt.buildpacket(self.network_id, self.device_id,
                                        self.sequence, self.payload)

        # make a temp server and run
        self.server_thread = UDPEchoServer("127.0.0.1", 16000)
        self.server_thread.daemon = True
        self.server_thread.start()

        # make a client and run
        self.client = udpxciever.Udpxciever("127.0.0.1", 16000)
        self.client.start()
        time.sleep(0.01)

    def test_packetsendrecievesingle(self):
        self.msgtwo = self.pkt.buildpacket(self.network_id, self.device_id,
                                           self.sequence, b'fdfgdf')
        # print("WritePacket at, " + str(util.gettimestamp()))
        self.client.writepacket(self.msg)
        time.sleep(0.01)
        ret_msg = self.client.readpacket()
        # print("retmsg at, " + str(util.gettimestamp()))

        self.assertEqual(self.msg, ret_msg, "Message1 not passed in transit")

    def test_packetsendrecievemulti(self):
        self.msgtwo = self.pkt.buildpacket(self.network_id, self.device_id,
                                           self.sequence, b'fdfgdf')
        # Send two messages
        self.client.writepacket(self.msg)
        self.client.writepacket(self.msgtwo)
        time.sleep(0.01)
        ret_msg = self.client.readpacket()
        ret_msgtwo = self.client.readpacket()

        self.assertEqual(self.msg, ret_msg, "Message1 not passed in transit")
        self.assertEqual(self.msgtwo, ret_msgtwo,
                         "Message2 not passed in transit")

    def test_packetsendrecievemultifragment(self):
        self.msgtwo = self.pkt.buildpacket(self.network_id, self.device_id,
                                           self.sequence, b'fdfgdf')
        self.client.writepacket(self.msg)
        # Send msgtwo in 2 parts
        self.client.writepacket(self.msgtwo[0:10])
        self.client.writepacket(self.msgtwo[10:])
        time.sleep(0.01)
        ret_msg = self.client.readpacket()
        ret_msgtwo = self.client.readpacket()

        self.assertEqual(self.msg, ret_msg, "Message1 not passed in transit")
        self.assertEqual(self.msgtwo, ret_msgtwo,
                         "Message2 not passed in transit")

    def test_getiface(self):
        iface = self.client.getiface()
        self.assertEqual(iface, "127.0.0.1", "Incorrect iface")

    def tearDown(self):
        # print("Term")
        self.client.close()
        self.server_thread.exit()
        time.sleep(0.01)

if __name__ == '__main__':
    unittest.main()
