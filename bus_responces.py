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
from imp_package import Package, PackageError

class BusResponceError(Exception):
    pass

class BusResponce(object):
    def __init__(self):
        self.tables = Tables()
        self.pkg    = Package()
    
    def get_long_ack(self,packet,serno):
        """ The counterpart of the bus_command get_long_ack().
        
        >>> bus = BusResponce()
        >>> pkg = a2b('0002001a7900a7')
        >>> bus.get_long_ack(pkg, 31002)
        True
        """
        responce = self.pkg.unpack(packet)
        return serno == responce['header']['serno']
    
    def get_short_ack(self,packet,serno):
        """ The counterpart of the bus_command get_short_ack().
        
        >>> bus = BusResponce()
        >>> pkg = a2b('24')
        >>> bus.get_short_ack(pkg, 31002)
        True
        """
        serno = struct.pack('<I', serno)[:-1]
        crc = self.pkg.calc_crc(serno)
        return crc == packet
    
    def get_range_ack(self,packet):
        """ The counterpart of the bus_command get_range_ack().
        
        >>> bus = BusResponce()
        >>> pkg = a2b('24')
        >>> bus.get_range_ack(pkg)
        True
        """
        return len(packet) == 1
    
    def get_negative_ack(self,packet):
        """ The counterpart of the bus_command get_negative_ack().
        
        >>> bus = BusResponce()
        >>> pkg = a2b('000805ffffffd91a79000042')
        >>> bus.get_negative_ack(pkg)
        31002
        """
        responce = self.pkg.unpack(packet)
        return struct.unpack('<I', responce['data'])[0]
    
    def set_parameter(self,packet,serno,table):
        """ The counterpart of the bus_command set_parameter().
        
        >>> bus = BusResponce()
        >>> pkg = a2b('0011001a790095')
        >>> bus.set_parameter(pkg,31002,'PROBE_CONFIGURATION_PARAMETER_TABLE')
        True
        """
        table = getattr(self.tables, table)
        responce = self.pkg.unpack(packet)
        command  = responce['header']['cmd']
        if not command == table.Table.Set:
            return False
        if not serno == responce['header']['serno']:
            return False
        return True
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
