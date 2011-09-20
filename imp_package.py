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
from binascii import b2a_hex as b2a, a2b_hex as a2b

class PackageError(Exception):
    pass

class Package(CRC):
    """ Class for packing, unpacking and checking IMPBus packages.
    
    Composing a IMPBus2 Package is done be the Package.pack() funktion
    and unpacking is done be the Package.unpack() funktion. While unpacking
    the CRCs and the given length of the provided IMPBUS package are checked.
    """
    
    def __init__(self):
        super(Package, self).__init__()
        self.DEBUG = True
    
    def _pack_data(self,data):
        if len(data)> 253:
            raise PackageError("Data block bigger than 252Bytes!")
        return data + self.calc_crc(data)
        
    def _unpack_data(self,data):
        if len(data)> 253:
            raise PackageError("Data block bigger than 252Bytes!")
        if not self.check_crc(data):
            raise PackageError("Package with faulty data CRC!")
        return data[:-1]
    
    def _pack_head(self,cmd,length,serno):
        state  = struct.pack('<B', 0xfd) # indicates IMP232N protocol version
        cmd    = struct.pack('<B', cmd)
        length = struct.pack('<B', length)
        serno  = struct.pack('<I', serno)[:-1]
        
        header = state + cmd + length + serno
        header = header + self.calc_crc(header)
        
        return header
    
    def _unpack_head(self,header):
        state  = struct.unpack('<B', header[0])[0]
        cmd    = struct.unpack('<B', header[1])[0]
        length = struct.unpack('<B', header[2])[0]
        serno  = struct.unpack('<I', header[3:6] + '\x00')[0]
        
        if not self.check_crc(header):
            raise PackageError("Package with faulty header CRC!")
        
        if state not in [0,253,255]:
            # TODO: Look up the real error msg!
            raise PackageError("Probe Error: {0}!".format(state))
        
        return {'state': state, 'cmd': cmd, 'length': length, 'serno': serno}
    
    def pack(self,serno,cmd,data=None):
        """ Funktion to create an IMPBUS2 package.
        
        The Package is created from serial number, command and
        data. Serno and command shold be INT! The data parameter
        should consist of a byte string, which has to be computed
        befor.
        
        Packing test: header // get_long_ack
        >>> p = Package()
        >>> package = p.pack(serno=33211,cmd=2)
        >>> b2a(package)
        'fd0200bb81002d'
        
        Packing test: header + data // get_erp_image, page1
        >>> p = Package()
        >>> data = a2b('ff01')
        >>> package = p.pack(serno=33211,cmd=60,data=data)
        >>> b2a(package)
        'fd3c03bb810083ff01df'
        
        Packing test: header + param_no + param_ad // get_serno
        >>> p = Package()
        >>> data = a2b('0100')
        >>> package = p.pack(serno=33211,cmd=10,data=data)
        >>> b2a(package)
        'fd0a03bb81009b0100c4'
        
        Packing test: header + param_no + param_ad + param // set_serno
        >>> p = Package()
        >>> data = a2b('0100bb810000')
        >>> package = p.pack(serno=33211,cmd=11,data=data)
        >>> b2a(package)
        'fd0b07bb8100580100bb810000fb'
        """
        
        if data:
            data    = self._pack_data(data)
            header  = self._pack_head(cmd,len(data),serno)
            package = header + data
        else:
            header = self._pack_head(cmd,0,serno)
            package = header
        
        return package
    
    def unpack(self,package):
        """ Funktion to unfold an IMPBUS2 package.
        
        Package is typically recieved from a connected probe.
        Returns a dict() with the decoded header information
        and the raw data part. The data part must be decoded
        extre, because additional information like data type
        and number of data sets is nedded.
        
        Unpacking test: header // responce to probe_module_long(33211)
        >>> p = Package()
        >>> package = a2b('000b00bb8100e6')
        >>> package = p.unpack(package)
        >>> package['header']
        {'state': 0, 'cmd': 11, 'length': 0, 'serno': 33211}
        
        Unpacking test: header + data // responce to get_serial(33211)
        >>> p = Package()
        >>> package = a2b('000a04bb810025bb810000cc')
        >>> package = p.unpack(package)
        >>> package['header']
        {'state': 0, 'cmd': 10, 'length': 4, 'serno': 33211}
        >>> struct.unpack('<I', package['data'])[0]
        33211
        """
        header = self._unpack_head(package[:7])
        data   = None
        if len(package) > 7:
            data = self._unpack_data(package[7:])
        package = {'header': header, 'data': data}
        
        return package

if __name__ == "__main__":
    import doctest
    doctest.testmod()
