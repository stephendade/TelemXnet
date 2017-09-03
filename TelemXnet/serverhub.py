#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  UDP Server hub
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
import threading
import socket
import select
import errno

# Via pip

# In this repo
from TelemXnet import unipacket
from TelemXnet import devicedict
from TelemXnet import util


class HubUDPServer(threading.Thread):
    """A UDP Server that relays any packets to and from clients"""
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.isExit = False

    def run(self):
        """Start running the UDP Server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(False)
        self.sock.bind((self.ip, self.port))
        self.devicedb = devicedict.Devicedict()
        while not self.isExit:
            ready = select.select([self.sock], [], [], 0.0001)
            if ready:
                try:
                    data, client = self.sock.recvfrom(util.getRxPacketSize())
                    # print("Echoing data back to " + str(client_address))
                    self.processPacket(data, client, self.sock)
                    # sent = sock.sendto(payload, client_address)
                except socket.error as excpt:
                    if excpt.errno in [errno.EAGAIN, errno.EWOULDBLOCK,
                                       errno.ECONNREFUSED]:
                        pass
                    else:
                        raise
        self.sock.close()

    def exit(self):
        """Shutdown the UDP server"""
        self.isExit = True

    def processPacket(self, data, client_address, socket):
        """Handle a recived packet - process it and send it out
        to any applicable clients"""

        # assume single complete packet has been recieved
        # send the id's to database
        pkt = unipacket.Unipacket()
        recv_data = pkt.recoverpacket(data)

        # bad packet
        if not recv_data:
            return

        # search through db for any clients to send to
        # UAV side id device 0-31, GCS side 32-63

        # Control packet if -ve and CL_BEGIN - add a client
        if recv_data.DeviceID < 0 and recv_data.Payload == b'CL_BEGIN':
            # control packet
            # print("Got Control Packet from " + str(recv_data.NetworkID) + "-"
            #  + str(-recv_data.DeviceID))
            self.devicedb.addremote(recv_data.NetworkID, -recv_data.DeviceID,
                                    client_address[0], client_address[1])
            return
        # control packet to remove client
        if recv_data.DeviceID < 0 and recv_data.Payload == b'CL_END':
            # control packet
            # print("Got Control Packet from " + str(recv_data.NetworkID) + "-"
            #  + str(-recv_data.DeviceID))
            self.devicedb.removeremote(recv_data.NetworkID, -recv_data.DeviceID)
            return
        # control packet for a server ping - just return the same packet
        if recv_data.DeviceID < 0 and recv_data.Payload == b'CL_SVRPING':
            #print("Got ping from seq " + str(recv_data.Sequence))
            self.senddevice(socket, recv_data.NetworkID, -recv_data.DeviceID,
                            data)
            return
        # print("Got " + str(recv_data.NetworkID) + "-" +
        # str(recv_data.DeviceID) + " from " + str(self.client_address[0]) +
        # ":" + str(self.client_address[1]))

        # only return non-server packets (ie. device_id >= 0)
        if recv_data.DeviceID >= 0 and recv_data.DeviceID < 32:
            # packet from UAS side
            for i in range(32, 63):
                self.senddevice(socket, recv_data.NetworkID, i, data)
        elif recv_data.DeviceID >= 0:
            # packet from GCS side
            for i in range(1, 31):
                self.senddevice(socket, recv_data.NetworkID, i, data)

    def senddevice(self, socket, network_id, device_id, data):
        """Send a packet to a client via a database lookup"""
        (ip_ret, port) = self.devicedb.getremote(network_id, device_id)

        if ip_ret and port:
            ret_address = (ip_ret, port)
            socket.sendto(data, ret_address)
            # print("Sent ")


class ServerHub():
    """This class is a small UAVNet server. All clients connect to this. The
    server will route packets as required to the clients"""

    def __init__(self, address="127.0.0.1", portin=16250):
        """Contstructor. Can override the IP and port that the server is
        bound to"""
        self.server_thread = HubUDPServer(address, portin)
        self.server_thread.daemon = True

    def run(self):
        """Start running the server"""
        self.server_thread.start()

    def close(self):
        """Shutdown the server"""
        self.server_thread.exit()
        # print("Server shutdown")
