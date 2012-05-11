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
from binascii import b2a_hex as b2a, a2b_hex as a2b

from imp_tables import Tables, TablesError
from imp_packages import Package, PackageError
from imp_crc import MaximCRC, MaximCRCError

class ResponceError(Exception):
    pass

class Responce(object):
    def __init__(self):
        self.tbl = Tables()
        self.pkg = Package()
        self.crc = MaximCRC()
        self.data_types = {
            0x00: '<{0}B', # 8-bit unsigned char
            0x01: '<{0}b', # 8-bit signed char
            0x02: '<{0}H', # 16-bit unsigned short
            0x03: '<{0}h', # 16-bit signed short
            0x04: '<{0}I', # 32-bit unsigned integer
            0x05: '<{0}i', # 32-bit signed integer
            0x06: '<{0}f', # 32-bit float
            0x07: '<{0}d'} # 64-bit double
    
    def get_long_ack(self, packet, serno):
        """ The counterpart of the command get_long_ack().
        
        >>> res = Responce()
        >>> pkg = a2b('0002001a7900a7')
        >>> res.get_long_ack(pkg, 31002)
        True
        """
        responce = self.pkg.unpack(packet)
        return serno == responce['header']['serno']
    
    def get_short_ack(self, packet, serno):
        """ The counterpart of the command get_short_ack().
        
        >>> res = Responce()
        >>> pkg = a2b('24')
        >>> res.get_short_ack(pkg, 31002)
        True
        """
        serno = struct.pack('<I', serno)[:-1]
        res_crc = self.crc.calc_crc(serno)
        return res_crc == packet
    
    def get_range_ack(self, packet):
        """ The counterpart of the command get_range_ack().
        
        >>> res = Responce()
        >>> pkg = a2b('24')
        >>> res.get_range_ack(pkg)
        True
        """
        return len(packet) == 1
    
    def get_negative_ack(self, packet):
        """ The counterpart of the command get_negative_ack().
        
        >>> res = Responce()
        >>> pkg = a2b('000805ffffffd91a79000042')
        >>> res.get_negative_ack(pkg)
        31002
        """
        responce = self.pkg.unpack(packet)
        return struct.unpack('<I', responce['data'])[0]
        
    def get_parameter(self, packet, table, param):
        """ The counterpart of the command get_parameter().
        
        >>> res = Responce()
        >>> pkg = a2b('000a051a7900181a79000042')
        >>> res.get_parameter(pkg, 'SYSTEM_PARAMETER_TABLE', 'SerialNum')
        (31002,)
        """
        data  = self.pkg.unpack(packet)['data']
        table = getattr(self.tbl, table)
        param = getattr(table, param)
        
        format = self.data_types[param.Type % 0x80]
        length = len(data)/struct.calcsize(format.format(1))
        
        return struct.unpack(format.format(length), data)
    
    def set_parameter(self, packet, serno, table):
        """ The counterpart of the bus_command set_parameter().
        
        >>> res = Responce()
        >>> pkg = a2b('0011001a790095')
        >>> res.set_parameter(pkg,31002,'PROBE_CONFIGURATION_PARAMETER_TABLE')
        True
        """
        responce = self.pkg.unpack(packet)
        command  = responce['header']['cmd']
        table = getattr(self.tbl, table)
        
        if not command == table.Table.Set:
            raise ResponceError("CMD dosen't match!")
        if not serno == responce['header']['serno']:
            raise ResponceError("Serno dosen't match!")
        
        return True
    
    def do_tdr_scan(self, packet):
        """ The counterpart of the command do_tdr_scan().
        
        Returns a nested dict() with the point number as key
        and an dict() with tdr and time as value. The TDR-Value
        is integer and the Time-Value is floating point.
        
        >>> res = Responce()
        >>> pkg = a2b('001e0b1a79006e112fc44e3702f3e7fb3dc5')
        >>> dat = res.do_tdr_scan(pkg)
        >>> dat[0]
        {'tdr': 17, 'time': 1.232423437613761e-05}
        >>> dat[1]
        {'tdr': 2, 'time': 0.12300100177526474}
        """
        data = self.pkg.unpack(packet)['data']
        data = [data[i:i+5] for i in range(0, len(data), 5)]
        scan = {}
        
        for point, tuble in enumerate(data):
            if not len(tuble) == 5:
                raise ResponceError("TDR Responce package has strange length!")
            scan_point         = {}
            scan_point['tdr']  = struct.unpack('<B', tuble[0])[0]
            scan_point['time'] = struct.unpack('<f', tuble[1:5])[0]
            scan[point]        = scan_point
        
        return scan
        
    def get_epr_image(self, packet):
        """ The counterpart of the command get_epr_image().
        
        Returns a list of the bytes as integer representing one
        page of the EEPROM read from the Module. EEPROM-Images
        mostly consists of multiple pages.
        
        >>> res = Responce()
        >>> pkg = a2b('003c0b1a790015112fc44e3702f3e7fb3dc5')
        >>> res.get_epr_image(pkg)
        [17, 47, 196, 78, 55, 2, 243, 231, 251, 61]
        """
        responce = self.pkg.unpack(packet)
        page = list()
        
        for byte in responce['data']:
            page.append(struct.unpack('<B', byte)[0])
        
        return page
    
    def set_epr_image(self, packet):
        """ The counterpart of the command set_epr_image().
        
        >>> res = Responce()
        >>> pkg = a2b('003d001a79004c')
        >>> res.set_erp_image(pkg)
        True
        """
        responce = self.pkg.unpack(packet)
        if not responce['header']['cmd'] == 61:
            raise ResponceError("CMD does not macht!")
        return True

if __name__ == "__main__":
    import doctest
    doctest.testmod()
