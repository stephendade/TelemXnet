#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Protocol compiler/decompiler
#  Class for defining a packet for TelemXnet
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
import hashlib
from construct import Struct, RawCopy, Byte, Bytes
from construct import Int8sb, Int16ub, this, Checksum

# Via pip
from cobs import cobsr

# in this repo


class Unipacket(object):
    """A single packet of data over UAVNet. A packet contains:
    -NetworkID (32 bytes)
    -Sending DeviceID (1-31 for UAV, 32-63 for GCS)
    -Sequence no (32 bytes) (at 1000 packets/sec, lasts 49 days)
    -Payload data (plus length)
    The packet includes a 8 byte CRC (sha-256 based)at the end.
    It also is put through COBS/R to ensure no 0x00 bytes in packet.
    Each packet has a 0x00 header
    Payload is a max 255-32-32-8-1-8 =  174 bytes
    """
    def __init__(self):
        self.protocol_header = b'\x00'
        self.message_format = Struct(
            "fields" / RawCopy(Struct(
                "NetworkID" / Bytes(32),
                "DeviceID" / Int8sb,
                "Sequence" / Int16ub,
                "Payload_length" / Byte,
                "Payload" / Bytes(this.Payload_length)
            )),
            "checksum" / Checksum(Bytes(4), lambda data:
                                  hashlib.sha256(data).digest()[0:4],
                                  this.fields.data),
        )

    def maxPayloadSize(self):
        """Returns the max payload size, 254 minus the headers"""
        return 254 - 32 - 8 - 16 - 1 - 4
        
    def buildpacket(self, _id, _device, _sequence, _payload):
        """Construct a packet based on the networkID, deviceID, timestamp
        and payload. Returns a series of bytes prepended with the header"""

        if (len(_id) != 32 or _device < -64 or _device > 64 or
                not isinstance(_sequence, int) or
                len(_payload) < 1):
            return None

        # create the message
        pkt_struct = dict(fields=dict(value=dict(NetworkID=_id,
                          DeviceID=_device, Sequence=_sequence,
                          Payload_length=len(_payload), Payload=_payload)))
        raw = self.message_format.build(pkt_struct)

        # put the message through cobs/r and put a header on the message
        return self.protocol_header + cobsr.encode(raw) + self.protocol_header

    def recoverpacket(self, pkt):
        """De-construct a packet, check it's CRC and return a struct
        containing the fields."""

        # check the header and footer is still here
        if pkt[0] != int.from_bytes(self.protocol_header, byteorder='big'):
            return None

        if pkt[len(pkt)-1] != int.from_bytes(self.protocol_header,
                                             byteorder='big'):
            return None

        # strip away the 0x00 header and de-cobs/r it
        recv_packet = cobsr.decode(pkt[1:-1])

        # parse through the structure
        try:
            pkt_struct = self.message_format.parse(recv_packet)
        except Exception:
            return None

        # verify the hash code
        chk = hashlib.sha256(pkt_struct.fields.data).digest()[0:4]
        if chk != pkt_struct.checksum:
            return None

        return pkt_struct.fields.value
