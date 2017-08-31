#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  It's a UDP server that Tx/Rx's information to the serverHub via
#  multiple udpxciever clients
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
import multiprocessing
from multiprocessing import Value
import time
import select

# Via pip

# In this repo
from TelemXnet import unipacket
from TelemXnet import udpxciever
from TelemXnet import util


class Clienthub(multiprocessing.Process):
    """This a a UDP server for sending and recieving data packets
    to a UAVNet server"""
    def __init__(self, local, remote, net_id, baseID):
        multiprocessing.Process.__init__(self)
        self.localaddport = local
        self.remaddport = remote
        self.net_id = net_id
        self.base_id = baseID
        self.client_ifaces_q = multiprocessing.Queue()
        self.endloop = Value('i', 0)
        self.pingbasetime = Value('l', 0)
        self.pinginprogress = Value('i', 0)
        self.ping_q = multiprocessing.Queue()

        self.pkt = unipacket.Unipacket()

    def addinterface(self, iface):
        """Add a network interface to the client
        Takes in the IP address of that interface"""
        self.client_ifaces_q.put("Add-" + iface)

    def removeinterface(self, iface):
        """Remove a network interface to the client
        Takes in the IP address of that interface"""
        self.client_ifaces_q.put("Rem-" + iface)

    def pinginterfaces(self):
        """Run a server ping on all ifaces. Also functions as a status/heartbeat
        checker. Returns initial list of all clients, then the ping responses"""
        retping = []
        alldevices = []
        if self.pingbasetime.value == 0:
            self.pingbasetime.value = util.gettimestamp()
        else:
            print("Ping already in process")

        # wait 500ms for ping returns
        for i in range(0, 500):
            time.sleep(0.001)
            if not self.ping_q.empty():
                resp = self.ping_q.get()
                if len(resp.split(',')) == 2:
                    alldevices.append(resp)
                else:
                    retping.append(resp)

        #figure out if any devices did not respond and put them as -1 in the ping list
        for ret in alldevices:
            i_d, iface = ret.split(',')
            found = False
            for pret in retping:
                if i_d + ',' + iface in pret:
                    found = True
            #not found
            if found == False:
                retping.append(i_d + ',' + iface + ',-1')
                
        # print("End ping")
        self.pingbasetime.value = 0
        self.pinginprogress.value = 0
        return retping

    def run(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serversocket.setblocking(False)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 10)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10)
        serversocket.bind(self.localaddport)
        udpclients = []
        udpclientdevid = []
        lastrxseq = -1
        seq_no = 0

        # print("Started")
        while self.endloop.value == 0:
            # sync with any changes to the client interfaces
            (udpclients, udpclientdevid) = self.sync_ifaces(udpclients,
                                                            udpclientdevid,
                                                            seq_no)
            # send out a server ping if required (and return list of all current clients)
            if self.pingbasetime.value != 0 and self.pinginprogress.value == 0:
                seq_no = self.sendallClients(udpclients, udpclientdevid, -1,
                                             seq_no, b'CL_SVRPING')
                self.pinginprogress.value = 1
                # print("Sending ping " + str(seq_no))
                for i in range(0, len(udpclients)):
                    self.ping_q.put(str(udpclientdevid[i]) + "," +
                                        str(udpclients[i].getiface()))
                    

            ready = select.select([serversocket], [], [], 0.0001)
            # if there is data from the local client, send it to the remote
            if ready[0]:
                data, address = serversocket.recvfrom(util.getRxPacketSize())

                # send to the all the clients...
                # print("Sending data")
                seq_no = self.sendallClients(udpclients, udpclientdevid, 1,
                                             seq_no, data)

            # poll the clients for any new data
            for i in range(0, len(udpclients)):
                # if client has data, compare to latest timestamp
                datarx = udpclients[i].readpacket()
                if datarx:
                    dec_msg = self.pkt.recoverpacket(datarx)
                    # check if it's a returned ping packet
                    if dec_msg.Payload == b'CL_SVRPING' and dec_msg.DeviceID < 0 and self.pinginprogress.value == 1:
                        deltatime = int((util.gettimestamp() -
                                         self.pingbasetime.value)/10)
                        self.ping_q.put(str(udpclientdevid[i]) + "," +
                                        str(udpclients[i].getiface()) +
                                        "," + str(deltatime))

                    # print("Got packet from serverhub["+ str(i) +"][" +
                    #      str(dec_msg.DeviceID) + "] " +
                    #      str(dec_msg.Timestamp) + ", " + str(lastrxtime))
                    # if this data is newer, send to local client and
                    # update the timestamp
                    # need to ensure it's a new packet and we have a
                    # connected local client
                    if dec_msg.Sequence > lastrxseq and ('address' in locals() or 'address' in globals()):
                        # print("rx packet")
                        lastrxseq = dec_msg.Sequence
                        serversocket.sendto(dec_msg.Payload, address)
        # close the socket on end
        if serversocket is not None:
            # send ending packets
            seq_no = self.sendallClients(udpclients, udpclientdevid, -1, seq_no,
                                         b'CL_END')
            # close the sockets - just remove the first item n times
            # (array reindexes each time)
            for i in range(0, len(udpclients)):
                udpclients[0].close()
                time.sleep(0.001)
                udpclients.remove(udpclients[0])
                udpclientdevid.remove(udpclientdevid[0])
            serversocket.close()
            # print("Ended")

    def sendallClients(self, udpclients, udpclientdevid, ctrl, seq_no, data):
        """Send data to server via all current ifaces"""
        for i in range(0, len(udpclients)):
            msg = self.pkt.buildpacket(self.net_id, ctrl * udpclientdevid[i],
                                       seq_no, data)
            udpclients[i].writepacket(msg)
        return seq_no + 1

    def sync_ifaces(self, udpclients, udpclientdevid, seq_no):
        """Runs inside thread. Syncs the iface queue with the internal
        vars, plus any CL_BEGINS and CL_ENDS"""
        while not self.client_ifaces_q.empty():
            ifacechange = self.client_ifaces_q.get()
            if ifacechange[0:4] == "Add-":
                # add client
                dev_id = self.base_id + len(udpclientdevid)
                udpclients.append(udpxciever.Udpxciever(self.remaddport[0],
                                                        self.remaddport[1],
                                                        ifacechange[4:]))
                udpclientdevid.append(dev_id)
                udpclients[len(udpclients)-1].start()
                time.sleep(0.001)
                msg = self.pkt.buildpacket(self.net_id, -dev_id,
                                           seq_no, b'CL_BEGIN')
                udpclients[len(udpclients)-1].writepacket(msg)
                # print("Client " + ifacechange[4:] + " added (" +
                # str(dev_id) + ")")
            elif ifacechange[0:4] == "Rem-":
                # remove client
                for i in range(0, len(udpclients)):
                    if udpclients[i].getiface() == ifacechange[4:]:
                        msg = self.pkt.buildpacket(self.net_id,
                                                   -udpclientdevid[i],
                                                   seq_no, b'CL_END')
                        udpclients[i].writepacket(msg)
                        # time.sleep(0.01)
                        udpclients[i].close()
                        udpclients.remove(udpclients[i])
                        # print("Client " + ifacechange[4:] + " removed (" +
                        # str(udpclientdevid[i]) + ")")
                        udpclientdevid.remove(udpclientdevid[i])
                        break
        # return new version of var
        return (udpclients, udpclientdevid)

    def join(self, timeout=None):
        if self.is_alive():
            self.endloop.value = 1
            multiprocessing.Process.join(self, timeout)
