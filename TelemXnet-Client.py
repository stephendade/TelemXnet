#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  End-user interface for a TelemXnet client
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
import argparse
import sys

# Via pip
import netifaces

# in this repo
from TelemXnet import clienthub


def ip4_addresses():
    """Get all the IPv4 addresses on this machine"""
    ip_list = []
    for interface in netifaces.interfaces():
        try:
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                ip_list.append(link['addr'])
        except KeyError:
            pass
    return ip_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--netid", help="The network ID (32 length string)", default=os.urandom(32))
    parser.add_argument("--remote", help="Server ip:port (ie 127.0.0.1:16250) or url:port (ie. google.com:16250", default='127.0.0.1:16250')
    parser.add_argument("--localport", help="Local port to listen on", type=int, default=14650)
    parser.add_argument("--localonly", help="Use localhost only", action="store_true")
    parser.add_argument("--mode", help="uas or gcs side", default='gcs')
    args = parser.parse_args()

    # check the network ID
    if len(args.netid) != 32:
        print("Error - Invalid network ID")
        sys.exit(0)

    # set the base of the device ID
    if args.mode == 'uas':
        base_id = 1
    else:
        base_id = 32

    # format the server address
    if len(args.remote.split(':')) != 2:
        print("Error - invalid remote")
        sys.exit(0)
    remoteserver = (args.remote.split(':')[0], int(args.remote.split(':')[1]))

    client = clienthub.Clienthub(("127.0.0.1", args.localport), remoteserver, args.netid.encode("utf8"), base_id)
    # print("Started Client")

    # check for interfaces to add
    if args.localonly:
        client.addinterface("127.0.0.1")
        print("Added " + "127.0.0.1")
    else:
        for iface in ip4_addresses():
            if str(iface) != "127.0.0.1":
                client.addinterface(str(iface))
                print("Added " + str(iface))

    # start the client
    client.start()
    # print("Started Client2")

    # while waiting for a ctrl+c, ping the server every 1 sec
    try:
        while True:
            time.sleep(1)
            p_ret = client.pinginterfaces()
            for dv in p_ret:
                i_d, iface, ptime = dv.split(',')
                print("Device " + str(i_d) + " (" + str(iface) + ") ping is " + str(ptime) + "ms")
    except KeyboardInterrupt:
        pass

    # then close it all down
    client.join()
    print("Closed Client")
