#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Measure packet efficiency
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
import os
import random

# Via pip

# in this repo
from TelemXnet import unipacket

if __name__ == '__main__':
    pkt = unipacket.Unipacket()
    device_id = random.randint(-64, 64)
    network_id = os.urandom(32)
    sequence = random.randint(0, 1000000)
    
    for i in [8, 16, 32, 64, 128, 255]:
        ppayload = os.urandom(i)
        msg = pkt.buildpacket(network_id, device_id, sequence, ppayload)
        efficiency = int(len(ppayload)*100 / len(msg))
        print("Eff of Payload=" + str(len(ppayload)) + " Packet=" + str(len(msg)) +
              " is " + str(efficiency) + "%")
