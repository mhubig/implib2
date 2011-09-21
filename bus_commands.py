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

class BusCommandError(Exception):
    pass

class BusCommand(object):
    """ COMMANDS TO CONTROL A IMPBUS2.
    
    After building-up a IMP232N-bus, it is necessary for the master to find
    out, which slaves are connected to the bus. This class provides the needed
    low level commands like get_long_acknowledge, get_short_acknowledge and
    get_negative_acknowledge.
    
    For more details please refer to the "Developers Manual, Data Transmission
    Protocol for IMPBUS2, 2008-11-18".
    """
    def __init__(self):
        self.tables = Tables()
        self.pkg    = Package()
        self.data_types = {
            0x00: '<{0}B', # 8-bit unsigned char
            0x01: '<{0}b', # 8-bit signed char
            0x02: '<{0}H', # 16-bit unsigned short
            0x03: '<{0}h', # 16-bit signed short
            0x04: '<{0}I', # 32-bit unsigned integer
            0x05: '<{0}i', # 32-bit signed integer
            0x06: '<{0}f', # 32-bit float
            0x07: '<{0}d'} # 64-bit double
        
    def get_long_ack(self,serno):
        """ GET LONG ACKNOWLEDGE
        
        This command with the number 2 will call up the slave which is
        addressed by its serial number. In return, the slave replies with
        a complete address block. It can be used to test the presence of
        a module in conjunction with the quality of the bus connection.
        
        >>> bus = BusCommand()
        >>> pkg = bus.get_long_ack(31001)
        >>> b2a(pkg)
        'fd02001979007b'
        """
        return self.pkg.pack(serno=serno,cmd=0x02)
        
    def get_short_ack(self,serno):
        """ GET SHORT ACKNOWLEDGE
        
        This command will call up the slave which is addressed by its serial
        number. In return, the slave replies by just one byte: The CRC of it's
        serial number. It is the shortest possible command without the transfer
        of any data block and the only one without a complete address block. It
        can be used to test the presence of a module.
        
        >>> bus = BusCommand()
        >>> pkg = bus.get_short_ack(31001)
        >>> b2a(pkg)
        'fd0400197900e7'
        """
        return self.pkg.pack(serno=serno,cmd=0x04)
        
    def get_range_ack(self,range):
        """ GET ACKNOWLEDGE FOR SERIAL NUMBER RANGE
        
        This command is very similar to the get_short_acknowledge command.
        However, it addresses not just one single serial number, but a serial
        number range. This value of byte 4 to byte 6 symbolizes a whole range
        according to the following pattern:
        
        +-----------+-------------+----------+---------------------+
        | High byte | Medium byte | Low byte |       Range         |
        +-----------+-------------+----------+---------------------+
        | 01000000  | 00000000    | 00000000 | 0x000000 - 0x7FFFFF |
        +-----------+-------------+----------+---------------------+
        | 11000000  | 00000000    | 00000000 | 0x800000 - 0xFFFFFF |
        +-----------+-------------+----------+---------------------+
        | usw.      |             |          |                     |
        
        The lowest "1" is not a part of the value but the (right) mark where
        the relevant value ends. All bits left of this mark are relevant, all
        bits right of this mark are non-relevant, including the mark itself.
        
        All modules within thus indicated range are addressed and will
        respond. The master can just detect if there is no response, which
        means that there is no slave within this range, or if there is a
        response of one or more slaves. The range must then be halved more
        and more to refine the search.
        
        two examples:
        =============
        
        start range: 10000000 00000000 00000000
        shift mark:   1000000 00000000 00000000
        lower half:  01000000 00000000 00000000 (old mark gets 0)
        higher half: 11000000 00000000 00000000 (old mark gets 1)
        
        start range: 11100000 00000000 00000000
        shift mark:     10000 00000000 00000000
        lower half:  11010000 00000000 00000000 (old mark gets 0)
        higher half: 11110000 00000000 00000000 (old mark gets 1)
        
        >>> bus = BusCommand()
        >>> rng = int(0b111100000000000000000000)
        >>> pkg = bus.get_range_ack(rng)
        >>> b2a(pkg)
        'fd06000000f0d0'
        """
        return self.pkg.pack(serno=range,cmd=0x06)
        
    def get_negative_ack(self):
        """ GET NEGATIVE ACKNOWLEDGE
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        
        >>> bus = BusCommand()
        >>> pkg = bus.get_negative_ack()
        >>> b2a(pkg)
        'fd0800ffffff60'
        """
        return self.pkg.pack(serno=16777215,cmd=0x08)
        
    def set_parameter(self,serno,table,param,value):
        """ COMMAND TO SET A PARAMETER.
        
        Command to write a parameter to one of the different parameter
        tables in the slave module. It will checkt if the value has the
        right type and if this parameter is writable, according tho the
        tables.
        
        >>> bus = BusCommand()
        >>> pkg = bus.set_parameter(31002,\
                'PROBE_CONFIGURATION_PARAMETER_TABLE',\
                'DeviceSerialNum',31003)
        >>> b2a(pkg)
        'fd11071a79002b0c001b790000b0'
        """
        table  = getattr(self.tables, table)
        param  = getattr(table, param)
        format = self.data_types[param.Type]
        
        param_no = struct.pack('<B', param.No)
        param_ad = struct.pack('<B', 0)
        param    = struct.pack(format.format(1), value)
        data     = param_no + param_ad + param
        
        package = self.pkg.pack(serno=serno,cmd=table.Table.Set,data=data)
        return package
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
