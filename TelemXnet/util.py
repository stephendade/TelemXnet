#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Misc utilities
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

# Via pip

# in this repo


def gettimestamp():
    """Get a timestamp in 100's of usec, must be <32bit"""
    return int(time.time()*10000)
    
def getRxPacketSize():
    """Return the number of bytes for a socket to rx"""
    return 254
