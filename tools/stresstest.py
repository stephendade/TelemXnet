#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  A stress test of TelemXnet to find the maximum packet rate
#  Userful for comparing the relative efficiency of code patches
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
import os
import socket
import random
import select

# Via pip

# in this repo
from TelemXnet import serverhub
from TelemXnet import clienthub

def streamTest(ExtGCS, ExtUAS, numPacket, delay, minsize, maxsize):
    """Runs a stress test of TelemXnet"""
    UASTx = b''
    GCSTx = b''
    GCSRx = b''
    UASRx = b''
    
    #Print out the test details
    print("---------------Test---------------")
    print("Testing " + str(numPacket) + " packets in " + str(numPacket*delay) + " sec")
    print("Packetsize is " + str(minsize) + " - " +str(maxsize) + " bytes")
    
    #send and receive a whole bunch of packets with
    #varying packet payload sizes
    for i in range(0, numPacket):
        j = random.randint(minsize, maxsize)
        pkt = os.urandom(j)
        GCSTx += pkt
        ExtGCS.sendto(pkt, ("127.0.0.1", 14650))
        
        pkt = os.urandom(j)
        UASTx += pkt
        ExtUAS.sendto(pkt, ("127.0.0.1", 14550))
        
        time.sleep(delay)
        
        readyGCS = select.select([ExtGCS], [], [], 0.0001)
        readyUAS = select.select([ExtUAS], [], [], 0.0001)
        if readyGCS[0]:
            GCSRx += ExtGCS.recv(1024)
        if readyUAS[0]:
            UASRx += ExtUAS.recv(1024)
            
    #and check how many packets we got
    GCSPercent = int((100 * len(GCSRx)) / len(UASTx))
    UASPercent = int((100 * len(UASRx)) / len(GCSTx))
    
    #Did we get all the packets back? If not, give stats
    if GCSPercent == 100 and UASPercent == 100:
        print("Pass")
    else:
        print("Got GCS " + str(len(GCSRx)) + "/" + str(len(UASTx)) + " packets")
        print("Got UAS " + str(len(UASRx)) + "/" + str(len(GCSTx)) + " packets")
        print("Got UAS=" + str(UASPercent) + "%, GCS=" + str(GCSPercent) + "%")

if __name__ == '__main__':
    # start a server
    srv = serverhub.ServerHub("127.0.0.1", 16250)
    srv.run()
    network_id = os.urandom(32)
    print("Server is up and running at 127.0.0.1:16250")

    # start a clienthub at each end
    GCSClient = clienthub.Clienthub(("127.0.0.1", 14650), ("127.0.0.1", 16250), network_id, 32)
    UASClient = clienthub.Clienthub(("127.0.0.1", 14550), ("127.0.0.1", 16250), network_id, 1)
    GCSClient.addinterface("127.0.0.1")
    UASClient.addinterface("127.0.0.1")
    GCSClient.start()
    print("GCS client is up and running at 127.0.0.1:14650")
    UASClient.start()
    print("UAS client is up and running at 127.0.0.1:14550")
    time.sleep(0.1)
    
    #Start some sockets for the UAS/GCS (with small Rx buffers)
    ExtGCS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ExtGCS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #ExtGCS.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 60)
    #ExtGCS.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 60)
    ExtGCS.settimeout(0.0001)
    ExtUAS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ExtUAS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #ExtUAS.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 60)
    #ExtUAS.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 60)
    ExtUAS.settimeout(0.0001)
    
    #ExtGCS.connect(("127.0.0.1", 14650))
    #ExtUAS.connect(("127.0.0.1", 14550))
    
    #small packet tests
    streamTest(ExtGCS, ExtUAS, 30, 0.01, 1, 50)
    streamTest(ExtGCS, ExtUAS, 300, 0.001, 1, 50)
    streamTest(ExtGCS, ExtUAS, 3000, 0.001, 1, 50)
    
    #medium size packet tests
    streamTest(ExtGCS, ExtUAS, 30, 0.01, 51, 150)
    streamTest(ExtGCS, ExtUAS, 300, 0.001, 51, 150)
    streamTest(ExtGCS, ExtUAS, 3000, 0.001, 51, 150)
    
    #large size packets
    streamTest(ExtGCS, ExtUAS, 30, 0.01, 151, 254)
    streamTest(ExtGCS, ExtUAS, 300, 0.001, 151, 254)
    streamTest(ExtGCS, ExtUAS, 3000, 0.001, 151, 254)
    
    # and wait for the user to end it
    # then close it all down
    ExtGCS.close()
    ExtUAS.close()
    GCSClient.join()
    UASClient.join()
    srv.close()

