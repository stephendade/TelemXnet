#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  A quick test over APM SITL
#  Takes in telemetry at 192.168.0.105:14550 and
#  gives it back out at 192.168.0.105:14650
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

# Via pip

# in this repo
from TelemXnet import serverhub
from TelemXnet import clienthub

if __name__ == '__main__':
    # start a server
    srv = serverhub.ServerHub("127.0.0.1", 16250)
    srv.run()
    network_id = os.urandom(32)
    print("Server is up and running at 127.0.0.1:16250")

    # start a clienthub at each end
    GCSClient = clienthub.Clienthub(("127.0.0.1", 14650), ("127.0.0.1", 16250), network_id, 32)
    UASClient = clienthub.Clienthub(("127.0.0.1", 14550), ("127.0.0.1", 16250), network_id, 1)
    GCSClient.addinterface("192.168.0.105")
    UASClient.addinterface("192.168.0.105")
    GCSClient.start()
    print("GCS client is up and running at 127.0.0.1:14650")
    UASClient.start()
    print("UAS client is up and running at 127.0.0.1:14550")
    time.sleep(0.1)

    # and wait for the user to end it
    input("Press Enter to exit...")

    # then close it all down
    GCSClient.join()
    UASClient.join()
    srv.close()
