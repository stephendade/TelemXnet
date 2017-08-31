#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Unit tests for clienthub
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
import os
import socket
#from gevent import socket
#from gevent import monkey

# Via pip

# in this repo
from TelemXnet import serverhub
from TelemXnet import clienthub


class ClienthubTestCase(unittest.TestCase):
    def setUp(self):
        # start a server
        self.srv = serverhub.ServerHub("127.0.0.1", 16250)
        self.srv.run()
        self.network_id = os.urandom(32)
        
        
        #and some external clients
        self.ExtGCS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ExtGCS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.ExtGCS.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 60)
        #self.ExtGCS.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 60)
        self.ExtGCS.settimeout(0.5)
        self.ExtUAS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ExtUAS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.ExtUAS.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 60)
        #self.ExtUAS.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 60)
        self.ExtUAS.settimeout(0.5)
        
        #and the clients themselves
        self.GCSClient = clienthub.Clienthub(("127.0.0.1", 14550), ("127.0.0.1", 16250), self.network_id, 33)
        self.UASClient = clienthub.Clienthub(("127.0.0.1", 14560), ("127.0.0.1", 16250), self.network_id, 2)
        time.sleep(0.05)

    def test_noOtherSide(self):
        # create two clients
        self.GCSClient.addinterface("127.0.0.1")
        self.GCSClient.start()
        time.sleep(0.001)

        # and send some packets
        self.ExtGCS.sendto(b'q87o73t4', ("127.0.0.1", 14550))
        time.sleep(0.01)

        # no response expected. The server just discards the packets if
        # it can't find somewhere the send them

    def test_TwoClients(self):
        # create two clients
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        self.GCSClient.start()
        self.UASClient.start()
        time.sleep(0.01)

        # and send some packets
        self.ExtGCS.sendto(b'q87o73t4', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'3984c0', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # get packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)
        
        self.assertEqual(b'3984c0', ret_gcs_msg, "Message UAS -> GCS not passed")
        self.assertEqual(b'q87o73t4', ret_uas_msg, "Message GCS -> UAS not passed")
        
        #and a second set of packets
        self.ExtGCS.sendto(b'o683bwp39846cb1p', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'3y85b21398p5bv3p12956c19p3cb', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # get packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)

        self.assertEqual(b'3y85b21398p5bv3p12956c19p3cb', ret_gcs_msg, "Message UAS -> GCS not passed")
        self.assertEqual(b'o683bwp39846cb1p', ret_uas_msg, "Message GCS -> UAS not passed")
        
    def test_TwoClientsmultiiface(self):
        # create two clients
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        self.GCSClient.start()
        self.UASClient.start()
        time.sleep(0.01)

        # and send some packets
        self.ExtGCS.sendto(b'q87o73t4', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'3984c0', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # get packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)

        self.assertEqual(b'3984c0', ret_gcs_msg, "Message UAS -> GCS not passed")
        self.assertEqual(b'q87o73t4', ret_uas_msg, "Message GCS -> UAS not passed")

        # add another iface, then repeat
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        time.sleep(0.01)
        
        # and send some packets
        self.ExtGCS.sendto(b'9p328b3n2', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'9p8368n5vc', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # get packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)

        self.assertEqual(b'9p8368n5vc', ret_gcs_msg, "Message UAS -> GCS not passed2")
        self.assertEqual(b'9p328b3n2', ret_uas_msg, "Message GCS -> UAS not passed2")

        # remove an iface, then go again
        self.GCSClient.removeinterface("127.0.0.1")
        self.UASClient.removeinterface("127.0.0.1")
        
        # and send some packets
        self.ExtGCS.sendto(b'93842n823', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'wp3498n5vwop8yriunrb98', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # get packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)

        self.assertEqual(b'wp3498n5vwop8yriunrb98', ret_gcs_msg, "Message UAS -> GCS not passed2")
        self.assertEqual(b'93842n823', ret_uas_msg, "Message GCS -> UAS not passed2")

    def test_TwoClientsNoIface(self):
        # create two clients
        self.GCSClient.start()
        self.UASClient.start()
        time.sleep(0.01)

        # and send some packets
        self.ExtGCS.sendto(b'q87o73t4', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'3984c0', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # now add some ifaces
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        time.sleep(0.01)

        # and send some packets that will actually be delivered this time
        self.ExtGCS.sendto(b'w9p83yc4b', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'37875c387b283b171', ("127.0.0.1", 14560))
        time.sleep(0.01)

        # get packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)

        self.assertEqual(b'37875c387b283b171', ret_gcs_msg, "Message UAS -> GCS not passed")
        self.assertEqual(b'w9p83yc4b', ret_uas_msg, "Message GCS -> UAS not passed")

    def test_ping(self):
        # create two clients
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        self.GCSClient.start()
        self.UASClient.start()
        time.sleep(0.01)

        # send some ping commands
        p_gcs = self.GCSClient.pinginterfaces()
        p_uav = self.UASClient.pinginterfaces()
        time.sleep(0.01)

        self.assertFalse(p_gcs is None, "Ping return is None")
        self.assertFalse(p_gcs is None, "Ping return is None")
        
        for dv in p_gcs:
            self.assertEqual(len(dv.split(',')), 3, "Ping return is Malformed")
            i_d, iface, ptime = dv.split(',')
            self.assertTrue(int(ptime) < 10, "ping time error")
            print("Device " + str(i_d) + " (" + str(iface) + ") ping is " + str(ptime) + "ms")
        for dv in p_uav:
            self.assertEqual(len(dv.split(',')), 3, "Ping return is Malformed")
            i_d, iface, ptime = dv.split(',')
            self.assertTrue(int(ptime) < 10, "ping time error")
            print("Device " + str(i_d) + " (" + str(iface) + ") ping is " + str(ptime) + "ms")

    def test_twonetworks(self):
        # finish building the first network
        self.GCSClient.addinterface("127.0.0.1")
        self.UASClient.addinterface("127.0.0.1")
        self.GCSClient.start()
        self.UASClient.start()
        time.sleep(0.01)

        # build a second network
        networktwo = os.urandom(32)
        self.GCSClienttwo = clienthub.Clienthub(("127.0.0.1", 14450), ("127.0.0.1", 16250), networktwo, 32)
        self.UASClienttwo = clienthub.Clienthub(("127.0.0.1", 14460), ("127.0.0.1", 16250), networktwo, 1)
        self.GCSClienttwo.addinterface("127.0.0.1")
        self.UASClienttwo.addinterface("127.0.0.1")
        self.GCSClienttwo.start()
        self.UASClienttwo.start()
        time.sleep(0.01)

        # create a second group of external clients
        self.ExtGCStwo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ExtGCStwo.settimeout(0.5)
        self.ExtUAStwo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ExtUAStwo.settimeout(0.5)
        time.sleep(0.01)

        # and send some packets
        self.ExtGCS.sendto(b'q87o73t4', ("127.0.0.1", 14550))
        self.ExtGCS.sendto(b'q87o73t4', ("127.0.0.1", 14550))
        self.ExtUAS.sendto(b'3984c0', ("127.0.0.1", 14560))
        self.ExtUAS.sendto(b'3984c0', ("127.0.0.1", 14560))
        self.ExtGCStwo.sendto(b'w93980586b', ("127.0.0.1", 14450))
        self.ExtGCStwo.sendto(b'w93980586b', ("127.0.0.1", 14450))
        self.ExtUAStwo.sendto(b'40mv089q38', ("127.0.0.1", 14460))
        self.ExtUAStwo.sendto(b'40mv089q38', ("127.0.0.1", 14460))
        time.sleep(0.01)

        # recieve the packets
        ret_gcs_msg = self.ExtGCS.recv(255)
        ret_uas_msg = self.ExtUAS.recv(255)
        ret_gcs_msg_two = self.ExtGCStwo.recv(255)
        ret_uas_msg_two = self.ExtUAStwo.recv(255)

        # and assert
        self.assertEqual(b'3984c0', ret_gcs_msg, "Message UAS -> GCS not passed")
        self.assertEqual(b'q87o73t4', ret_uas_msg, "Message GCS -> UAS not passed")
        self.assertEqual(b'40mv089q38', ret_gcs_msg_two, "Message2 UAS -> GCS not passed")
        self.assertEqual(b'w93980586b', ret_uas_msg_two, "Message2 GCS -> UAS not passed")

    def tearDown(self):
        self.ExtGCS.close()
        self.GCSClient.join()
        self.ExtUAS.close()
        self.UASClient.join()
        
        try:
            # close down the second network, if used
            self.ExtGCStwo.close()
            self.GCSClienttwo.join()
            self.ExtUAStwo.close()
            self.UASClienttwo.join()
        except AttributeError:
            pass
        self.srv.close()
        time.sleep(0.01)

if __name__ == '__main__':
    unittest.main()
