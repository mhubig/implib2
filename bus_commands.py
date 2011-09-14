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

from imp_tables import Tables, TablesException
from imp_packets import Packets, PacketsException

class BusCommandsException(Exception):
    pass

class BusCommands(Packets, Tables):
    """ COMMANDS TO CONTROL A IMPBUS2.
    
    After building-up a IMP232N-bus, it is necessary for the master to find
    out, which slaves are connected to the bus. This class provides the needed
    low level commands like get_long_acknowledge, get_short_acknowledge and
    get_negative_acknowledge.
    
    For more details please refer to the "Developers Manual, Data Transmission
    Protocol for IMPBUS2, 2008-11-18".
    
    >>> bus 
    
    """
    def __init__(self):
        self.DEBUG = False
        Packets.__init__(self)
        Tables.__init__(self)
        
    def get_long_acknowledge(self,serno):
        """ GET LONG ACKNOWLEDGE
        
        This command with the number 2 will call up the slave which is
        addressed by its serial number. In return, the slave replies with
        a complete address block. It can be used to test the presence of
        a module in conjunction with the quality of the bus connection.
        
        >>> bus = BusCommands()
        >>> print bus.get_long_acknowledge(31001)
        fd02001979007b
        """
        return self.pack(serno=serno,cmd=0x02)
        
    def get_short_acknowledge(self,serno):
        """ GET SHORT ACKNOWLEDGE
        
        This command will call up the slave which is addressed by its serial
        number. In return, the slave replies by just one byte: The CRC of it's
        serial number. It is the shortest possible command without the transfer
        of any data block and the only one without a complete address block. It
        can be used to test the presence of a module.
        
        >>> bus = BusCommands()
        >>> print bus.get_short_acknowledge(31001)
        fd0400197900e7
        """
        return self.pack(serno=serno,cmd=0x04)
        
    def get_acknowledge_for_serial_number_range(self,range):
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
        
        >>> bus = BusCommands()
        >>> range = int(0b111100000000000000000000)
        >>> print bus.get_acknowledge_for_serial_number_range(range)
        fd06000000f0d0
        """
        return self.pack(serno=range,cmd=0x06)
        
    def get_negative_acknowledge(self):
        """ GET NEGATIVE ACKNOWLEDGE
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        
        >>> bus = BaseCommands()
        >>> print bus.get_negative_acknowledge()
        fd0800ffffff60
        """
        return self.pack(serno=16777215,cmd=0x08)
        
    def set_parameter(self, serno, table, param, value):
        """ COMMAND TO SET A PARAMETER.

        Command to write a parameter to one of the different parameter
        tables in the slave module. It will checkt if the value has the
        right type and if this parameter is writable, according tho the
        tables.

        TODO: Check the value type!

        >>> module = ModuleCommands()
        >>> print module.set_parameter(31002,\
                'PROBE_CONFIGURATION_PARAMETER_TABLE',\
                'DeviceSerialNum',31003)
        fd11071a79002b0c000000791bc4
        """
        table = getattr(self, table)
        param = getattr(table, param)

        value = '%x' % value
        value = value.zfill(param.Length*2)

        #if not param.writeable():
        #    raise ModuleCommandsException('Parameter is not writeable!')

        if not len(value)/2 == param.Length:
            raise ModuleCommandsException('Parameter has the wrong length!')

        package = self.pack(serno, table.Table.Set, param.No, value)
        return package
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
