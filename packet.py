#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import binascii
from crc import CRC

class PacketError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Packet(object):
    """ Class for packing, unpacking and checking IMPBus packages.
    
    Packing is done be the Packet.pack() funktion and unpacking is
    done be the Packet.unpack() funktion. While unpacking the CRCs
    and the given length of the provided IMPBUS package are checked.
    
    >>> from packet import Packet,PacketError
    >>> p = Packet()
    >>> packet = p.pack(serno=0,cmd=0x15,no_param=0x01,param=30521)
    >>> stuff = p.unpack(packet)
    >>> stuff['header']
    {'state': '0xfd', 'cmd': '0x15', 'length': 5, 'serno': 0}
    >>> stuff['data']
    {'no_param': '0x1', 'ad_param': '0x0', 'param': '7739'}
    >>> packet = p.pack(serno=30521,cmd=0x15)
    >>> stuff = p.unpack(packet)
    >>> stuff['header']
    {'state': '0xfd', 'cmd': '0x15', 'length': 0, 'serno': 30521}
    >>> stuff['data']
    """
    
    def __init__(self):
         self._crc  = CRC()
    
    def _hexhex(self,str):
        return hex(int(str, 16))
    
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
        serno = int(header[10:12]+ header[8:10] + header[6:8], 16)
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
        no_param = self._hexhex(data[0:2])
        ad_param = self._hexhex(data[2:4])
        param = data[4:]
        return {'no_param': no_param, 'ad_param': ad_param, 'param': param}
    
    def _pack_data(self, no_param, param, ad_param=None):
        if not ad_param: ad_param = '00'
        no_param = '%02X' % no_param
        param = '%X' % param
        data = no_param + ad_param + param
        data = data + self._crc.calc(data)
        return data       
    
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
             
        if not self._crc.check(header):
            raise PacketError("Received a package with faulty header!")
                   
        if not data:
            if not data_length == 0:
                raise PacketError("Length of data block shold be zero!")
        else:
            if len(data) > 504:
                raise PacketError("Data block bigger than 252Bytes!")
            if len(data) != data_length:
                raise PacketError("Length of data block dosn't match!")
            if not self._crc.check(data):
                raise PacketError("Received a package with faulty data!")
            data = data[:-2] # remove CRC
                
        header = header[:-2] # remove CRC
        
        return header, data
         
    def pack(self, serno, cmd, no_param=None, param=None, ad_param=None):
        """ Funktion to create an IMPBUS package.
        
        Package is created from serial number, command and data
        string. serno shold be int, cmd hex and data should be a
        hex-string!
        """
        state = 'FD' # indicates IMP232N protocol version
        serno = '%06X' % serno
        cmd = '%02X' % cmd
        serno = serno[4:6] + serno[2:4] + serno[0:2]
        
        if no_param:
            data = self._pack_data(no_param, param, ad_param)
            length = '%02X' % (len(data) / 2)
            header = state + cmd + length + serno
            header = header + self._crc.calc(header)
            packet = header + data
        else:
            length = '00'
            header = state + cmd + length + serno
            header = header + self._crc.calc(header)
            packet = header
        
        return binascii.a2b_hex(packet)
        
    def unpack(self, packet):
        """ Funktion to unfold an IMPBUS package.
        
        Package is typically recieved from a connected probe. Returns
        a dict containing state [hex], command [hex], length [hex], serial
        number [int] and data [hex-string].
        """
        packet = binascii.b2a_hex(packet)
        header, data = self._check(packet)
        header = self._split_header(header)
        if data: data = self._split_data(data)
        
        return {'header': header, 'data': data}
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
