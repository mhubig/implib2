#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from crc import CRC

class PacketError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Packet(object):
    """Class for packing and unpacking IMPBus packages."""
    
    def __init__(self):
         self._crc  = crc.CRC()
        
    def _cut_data(self, packet):
        # Data is starting at byte 7 that is char 14 of my
        # ASCII HEX string. The length of the DATA part is
        # coded at byte 2 that is char 4 & 5 of my ASCII HEX
        # string       
        data_start  = 14
        data_length = 2 * int(packet[4:6], 16)
        data_end    = data_start + data_length
        return packet[data_start:data_end]

    def _cut_header(self, packet):
        # Cut's out the header. The header is
        # within the first 7 bytes.
        header_start = 0
        header_lenth = 14
        return packet[header_start:header_lenth]

    def _check(self, packet):
        # check if the package is faulty, since there are
        # packages without data and only header, headle them
        # seperate.
        if len(packet) == 14:
            header = packet
            data   = None
        else:
            header = self._cut_header(packet)
            data   = self._cut_data(packet)

        if not self._crc.check(header):
            raise PackageError("Received a faulty header string!")
            
        if data and not self._crc.check(data):
            raise PackageError("Received a faulty data string!")
        
        return header, data
        
    def pack(self, serno, cmd, data=None):
        state = 'FD' # indicates IMP232N protocol version
        length = len(data) / 2
        serno = "%06X" % serno
        header = state + cmd + length + serno
        header = header + self._crc.calc(header)
        if data:
            data = data + self._crc.calc(data)
            packet =  binascii.a2b_hex(header + data)
        else:
            packet = binascii.a2b_hex(header)
        return packet
        
    def unpack(self, packet):
        packet = binascii.b2a_hex(packet)
        self._check(packet)
        header = self._cut_header(packet)
        data = self._cut_data(packet)
