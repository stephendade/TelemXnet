#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  End-user interface for a TelemXnet server
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
from TelemXnet import serverhub


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", help="The IP of the network adapter to run on", default="127.0.0.1")
    parser.add_argument("--port", help="The server port", type=int, default=16250)
    args = parser.parse_args()

    srv = serverhub.ServerHub(args.ip, args.port)
    
    #start the server
    srv.run()
    print("Server running")

    # while waiting for a ctrl+c, sleep
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    # then close it all down
    srv.close()
    print("Closed Server")
