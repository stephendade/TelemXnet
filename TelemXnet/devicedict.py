#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Device database
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

# Via pip

# In this repo


class Devicedict():
    """A dictionary of devices in the server, where the key is
    networkID-deviceID and the value is a (ip port) tuple"""
    def __init__(self):
        self.dict = {}

    def addremote(self, network, device, _ip, _port):
        """Add a new remote to the database"""
        # print("Mapped Dev-" + str(device) + " to" + str(ip) + ":" + str(port))
        self.dict[str(network) + "-" + str(device)] = (_ip, _port)

    def getremote(self, network, device):
        """Get the (ip, port) of a device, return
        (None, None) if device not found"""
        try:
            return self.dict[str(network) + "-" + str(device)]
        except KeyError:
            return (None, None)
            
    def removeremote(self, network, device):
        """Remove a remote from the database"""
        try:
            del self.dict[str(network) + "-" + str(device)]
        except KeyError:
            return None
