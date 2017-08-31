#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Client for transmitting and receiving UDP packets to server
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
import socket
import select
import errno
import queue
import threading
import multiprocessing
import collections

# Via pip

# In this repo
from TelemXnet import util

class Udpxciever(threading.Thread):
    """This a a UDP transciever for sending and recieving data packets
    to a UAVNet server"""
    def __init__(self, address, port, iface="127.0.0.1"):
        threading.Thread.__init__(self)
        self.iface = iface
        self.rem = (address, port)
        self.rxbuffer = b''
        self.packetsRx = collections.deque()
        self.packetsTx = collections.deque()
        # self.manager = Manager()
        self.protocol_header = b'\x00'
        self.isExit = False

    def run(self):
        """Start the transciever"""
        self.xmittersocket = udpclient(self.rem[0], self.rem[1], self.iface)
        
        #keep trying to rx packets...
        while not self.isExit:
            curdata = self.xmittersocket.recv()
            if curdata:
                self.rxbuffer  += curdata
                #print("buf is " + str(self.rxbuffer) + "chars")
                
            if self.protocol_header in self.rxbuffer:
                indStart = self.rxbuffer.find(self.protocol_header)
                indEnd = self.rxbuffer.find(self.protocol_header, indStart+1)
                
                if indStart != -1 and indEnd != -1:
                    # print("rxqueue put at, " + str(util.gettimestamp()))
                    nxtpkt = self.rxbuffer[indStart:indEnd+1]
                    if len(self.rxbuffer) > indEnd:
                        self.rxbuffer = self.rxbuffer[indEnd+1:]
                    else:
                        self.rxbuffer = b''
                    self.packetsRx.append(nxtpkt)
                    
            if len(self.packetsTx) > 0:
                self.xmittersocket.write(self.packetsTx.popleft())
                
        self.xmittersocket.close()

    def getiface(self):
        """Get the IP interface used by this transciever"""
        return self.iface

    def close(self):
        """Close this transciever"""
        self.isExit = True

    def writepacket(self, packet):
        """Transmit a data packet
        """
        # print("TXQueue put at, " + str(util.gettimestamp()))
        # self.xmittersocket.write(packet)
        self.packetsTx.append(packet)

    def readpacket(self):
        """Read the latest data packet from the queue
        Only returns a single packet at a time
        """
        if len(self.packetsRx) > 0:
            return self.packetsRx.popleft()
        else:
            return None


class udpclient():
    '''A UDP socket'''
    def __init__(self, ip, port, iface):
        self.port = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port.bind((iface, 0))
        self.port.setblocking(False)
        #self.port.settimeout(0.001)
        self.ip = ip
        self.portr = port
        self.port.connect((self.ip, self.portr))

    def close(self):
        """Close the socket"""
        self.port.close()

    def recv(self):
        """Return any data in the buffer. If not data in buffer, return null"""
        #r, _, _ = select.select([self.port], [], [], 0.0001)
        ready = select.select([self.port], [], [], 0.0001)
        if not ready:
            return None

        try:
            data, new_addr = self.port.recvfrom(util.getRxPacketSize())
        except socket.error as excpt:
            if excpt.errno in [errno.EAGAIN, errno.EWOULDBLOCK,
                               errno.ECONNREFUSED]:
                return None
            raise
        return data

    def write(self, buf):
        """Write data to the socket"""
        try:
            self.port.sendto(buf, (self.ip, self.portr))
        except socket.error:
            pass
