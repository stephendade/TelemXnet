#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for serverhub
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

# Via pip

# in this repo
from TelemXnet import unipacket
from TelemXnet import udpxciever
from TelemXnet import serverhub
from TelemXnet import util


class ServerhubTestCase(unittest.TestCase):
    def setUp(self):
        # testing the serrver
        # print("Booting Server")
        self.srv = serverhub.ServerHub()
        self.srv.run()

        # print("Booting client")
        self.clientUAS = udpxciever.Udpxciever("127.0.0.1", 16250)
        self.clientGCS = udpxciever.Udpxciever("127.0.0.1", 16250)
        self.clientUAS.start()
        self.clientGCS.start()
        time.sleep(0.1)

    def test_twoclientssinglepacket(self):
        # encode
        network_id = os.urandom(32)
        device_idUAS = random.randint(1, 31)
        device_idGCS = random.randint(32, 63)
        msgUAS = self.makePacketrnd(network_id, device_idUAS)
        msgGCS = self.makePacketrnd(network_id, device_idGCS)

        # send initial packets
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b"CL_BEGIN"))
        self.clientGCS.writepacket(self.makePacketrnd(network_id, -device_idGCS,
                                                      b"CL_BEGIN"))

        # send data packets
        basetime = util.gettimestamp()
        self.clientUAS.writepacket(msgUAS)
        self.clientGCS.writepacket(msgGCS)
        time.sleep(0.001)

        # rx packets, with performance counters
        retmsgGCS = self.readpackettime(self.clientGCS, basetime)
        retmsgUAS = self.readpackettime(self.clientUAS, basetime)

        # send end packets
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b"CL_END"))
        self.clientGCS.writepacket(self.makePacketrnd(network_id, -device_idGCS,
                                                      b"CL_END"))
        time.sleep(0.001)

        # and assert
        self.assertEqual(msgUAS, retmsgGCS, "Message UAS -> GCS incorrect")
        self.assertEqual(msgGCS, retmsgUAS, "Message GCS -> UAS incorrect")

    def test_singleclientnoendpoint(self):
        # encode
        network_id = os.urandom(32)
        device_idUAS = random.randint(1, 31)
        msgUAS = self.makePacketrnd(network_id, device_idUAS)

        # send initial packets (single endpoint)
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b"CL_BEGIN"))

        # send a data packet
        self.clientUAS.writepacket(msgUAS)
        time.sleep(0.05)

        # rx packets, with performance counters
        retmsgGCS = self.clientGCS.readpacket()
        retmsgUAS = self.clientUAS.readpacket()

        # send end packet (single endpoint)
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b"CL_END"))
        time.sleep(0.001)

        # and assert
        self.assertEqual(None, retmsgGCS, "No Message UAS -> GCS incorrect")
        self.assertEqual(None, retmsgUAS, "No Message GCS -> UAS incorrect")

    def test_twoclientsmultipacket(self):
        # encode
        network_id = os.urandom(32)
        device_idUAS = random.randint(1, 31)
        device_idGCS = random.randint(32, 63)
        msgUASOne = self.makePacketrnd(network_id, device_idUAS)
        msgGCSOne = self.makePacketrnd(network_id, device_idGCS)
        msgUASTwo = self.makePacketrnd(network_id, device_idUAS)
        msgGCSTwo = self.makePacketrnd(network_id, device_idGCS)

        # send initial packets
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b'CL_BEGIN'))
        self.clientGCS.writepacket(self.makePacketrnd(network_id, -device_idGCS,
                                                      b'CL_BEGIN'))

        # send data packets
        basetime = util.gettimestamp()
        self.clientUAS.writepacket(msgUASOne)
        self.clientUAS.writepacket(msgUASTwo)
        self.clientGCS.writepacket(msgGCSOne)
        self.clientGCS.writepacket(msgGCSTwo)
        time.sleep(0.001)

        # rx packets, with performance counters
        retmsgGCSOne = self.readpackettime(self.clientGCS, basetime)
        retmsgGCSTwo = self.readpackettime(self.clientGCS, basetime)
        retmsgUASOne = self.readpackettime(self.clientUAS, basetime)
        retmsgUASTwo = self.readpackettime(self.clientUAS, basetime)

        # send end packets
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b"CL_END"))
        self.clientGCS.writepacket(self.makePacketrnd(network_id, -device_idGCS,
                                                      b"CL_END"))
        time.sleep(0.001)

        # and assert
        self.assertEqual(msgUASOne, retmsgGCSOne, "Message1 UAS -> GCS incorr")
        self.assertEqual(msgGCSOne, retmsgUASOne, "Message1 GCS -> UAS incorr")
        self.assertEqual(msgUASTwo, retmsgGCSTwo, "Message2 UAS -> GCS incorr")
        self.assertEqual(msgGCSTwo, retmsgUASTwo, "Message2 GCS -> UAS incorr")

    def test_serverping(self):
        # encode
        network_id = os.urandom(32)
        device_idUAS = random.randint(1, 31)

        # send initial packets
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b'CL_BEGIN'))

        # send ping packet
        pingpkt = self.makePacketrnd(network_id, -device_idUAS, b'CL_SVRPING')
        starttime = util.gettimestamp()
        self.clientUAS.writepacket(pingpkt)
        time.sleep(0.001)
        retping = self.readpackettime(self.clientUAS, starttime)

        # send end packets
        self.clientUAS.writepacket(self.makePacketrnd(network_id, -device_idUAS,
                                                      b'CL_END'))
        time.sleep(0.001)
        self.assertEqual(retping, pingpkt, "MessageP GCS -> GCS incorr")

    def makePacketrnd(self, network_id, device_id, _payload=b''):
        seq = random.randint(0, 1000000)
        if _payload == b'':
            payload = os.urandom(16)
        else:
            payload = _payload

        pkt = unipacket.Unipacket()
        msg = pkt.buildpacket(network_id, device_id, seq, payload)

        return msg

    def readpackettime(self, client, basetime):
        ret_msg = None
        # print("Going for timing")
        while ret_msg is None and util.gettimestamp() < (basetime+20000):
            ret_msg = client.readpacket()
        endtime = util.gettimestamp()
        delaytime = int((endtime/10 - basetime/10))
        #print("Response time is " + str(delaytime) + "ms")
        self.assertTrue(delaytime < 10, "Response time is too long")
        return ret_msg

    def tearDown(self):
        # print("Term")
        self.clientUAS.join()
        self.clientGCS.join()
        self.srv.close()
        time.sleep(0.1)

if __name__ == '__main__':
    unittest.main()
