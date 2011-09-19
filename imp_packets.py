#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011, Markus Hubig <mhubig@imko.de>

This file is part of IMPLib2 a small Python library implementing
the IMPBUS-2 data transmission protocol.

IMPLib2 is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

IMPLib2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with IMPLib2. If not, see <http://www.gnu.org/licenses/>.
"""

import struct
from tools_crc import CRC

class PacketsException(Exception):
    pass

class Packets(CRC):
    """ Class for packing, unpacking and checking IMPBus packages.
    
    Packing is done be the Packet.pack() funktion and unpacking is
    done be the Packet.unpack() funktion. While unpacking the CRCs
    and the given length of the provided IMPBUS package are checked.
    
    >>> p = IMPPacket()
    >>> packet = p.pack(serno=0,cmd=0x15,no_param=0x01,param='7739')
    >>> stuff = p.unpack(packet)
    >>> stuff['header']
    {'state': '0xfd', 'cmd': '0x15', 'length': 5, 'serno': 0}
    >>> stuff['data']
    '01007739'
    >>> packet = p.pack(serno=30521,cmd=0x15)
    >>> stuff = p.unpack(packet)
    >>> stuff['header']
    {'state': '0xfd', 'cmd': '0x15', 'length': 0, 'serno': 30521}
    >>> stuff['data']
    """
    
    def __init__(self):
        self.DEBUG = True
        CRC.__init__(self)
        
        self.data_types = {
            0x00: '>{0}B', # 8-bit unsigned char
            0x01: '>{0}b', # 8-bit signed char
            0x02: '>{0}H', # 16-bit unsigned short
            0x03: '>{0}h', # 16-bit signed short
            0x04: '>{0}I', # 32-bit unsigned integer
            0x05: '>{0}i', # 32-bit signed integer
            0x06: '>{0}f', # 32-bit float
            0x07: '>{0}d'} # 64-bit double
        
    def _hexhex(self,str):
        return hex(int(str, 16))
    
    def _reflect_bytes(self, data):
        """
        reflect a hex asscii string, i.e. reverts the byte order.
        """
        reflected = ''
        length = len(data)

        if not length % 2 == 0:
            raise PacketsException("ERROR: Odd length of string: %s" % data)

        while length > 0:
            reflected += data[length-2:length]
            length = length - 2
        return reflected
    
    def _cut_header(self, packet):
        # Cut's out the header. The header is
        # within the first 7 bytes.
        header_start = 0
        header_end = 14
        return packet[header_start:header_end]
        
    def _split_header(self, header):
        state = self._hexhex(header[0:2])
        cmd = self._hexhex(header[2:4])
        length = int(header[4:6], 16)
        serno = int(self._reflect_bytes(header[6:12]), 16)
        return {'state': state, 'cmd': cmd, 'length': length, 'serno': serno}

    def _cut_data(self, packet):
        # Data is starting at byte 7 that is char 14 of my
        # ASCII HEX string. The length of the DATA part is
        # coded at byte 2 that is char 4 & 5 of my ASCII HEX
        # string       
        data_start = 14
        data_end = len(packet)
        return packet[data_start:data_end]

    def _split_data(self, data):
        # useless for unpacking recived packages, cause
        # the format depends on the command ... ;-(
        no_param = self._hexhex(data[0:2])
        ad_param = self._hexhex(data[2:4])
        param = data[4:]
        return {'no_param': no_param, 'ad_param': ad_param, 'param': param}

    def _pack_data(self, param_type=0, param_no=0, param=None):
        # param is optional because of the get commands
        # UPDATED!
        param_no = struct.pack('>B', no_param)
        param_ad = struct.pack('>B', 0)
  
        if not param:
            data = param_no + param_ad
            data = data + self.calc_crc(data)
        else:
            param_type = param_type % 80
            format = self.data_types[param_type]
            if isinstance(param, (list, tuple, set)):
                param = pack(format.format(len(param)), param)
            param = pack(format.format(1), param)
            data = param_no + param_ad + param
            data = data + self.calc_crc(data)
        return data

    def _check_header(self,header):
        if not self.check_crc(header):
            raise PacketsException("Package with faulty header CRC!")
        status = header[0:2]
        if status not in ['00','fd', 'ff']:
            raise PacketsException("Package with error status: %i!"
                % int(status,16))
        return header[:-2]

    def _check_data(self,data):
        if not self.check_crc(data):
            raise PacketsException("Package with faulty data CRC!")
        if len(data[:-2]) > 504:
            raise PacketsException("Data block bigger than 252Bytes!")
        return data[:-2]

    def _check(self, packet):
        # check if the package is faulty, since there are
        # packages without data and only header, headle them
        # seperate. Returns header & data *without* CRC!
        if len(packet) == 14:
            header = packet
            data   = None
        else:
            header = self._cut_header(packet)
            data   = self._cut_data(packet)

        data_length = 2 * int(packet[4:6], 16)
        header = self._check_header(header)

        if not data:
            if not data_length == 0:
                raise PacketsException("Length of data block should be zero!")
        else:
            if len(data) != data_length:
                raise PacketsException("Length of data block dosn't match!")
            data = self._check_data(data)
        return header, data

    def pack(self,serno=00000,cmd=0x00,param_type=0x00,param_no=None,param=None):
        """ Funktion to create an IMPBUS2 package.
        
        Package is created from serial number, command and data
        string. serno shold be [int/hex], cmd [hex/int] and data
        should be a hex-string!
        """
        
        state = struct.pack('>B', 0xfd) # indicates IMP232N protocol version
        serno = struct.pack('>I', serno)[1:4]
        cmd   = struct.pack('>B', cmd)
        
        if param_no:
            data = self._pack_data(param_type, param_no, param)
            length = struct.pack('>B', len(data))
            header = state + cmd + length + serno
            header = header + self.calc_crc(header)
            packet = header + data
        else:
            length = struct.pack('>B', 0xfd)
            header = state + cmd + length + serno
            header = header + self.calc_crc(header)
            packet = header

        return packet

    def unpack(self, packet):
        """ Funktion to unfold an IMPBUS2 package.
        
        Package is typically recieved from a connected probe.
        Returns a dict containing state [hex], command [hex],
        length [hex], serial number [int] and data [hex-string].
        """
        header, data = self._check(packet)
        header = self._split_header(header)
        header['data'] = data
        return header

if __name__ == "__main__":
    import doctest
    doctest.testmod()
