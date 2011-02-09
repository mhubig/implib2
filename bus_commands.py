#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (c) 2009-2012, Markus Hubig <mhubig@imko.de>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from tables import Tables, TablesException
from packet import Packet, PacketException

class BaseCommandsException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BaseCommands(Packet, Tables):
    """ COMMANDS TO CONTROL BUS.
    
    After building-up a IMP232N-bus, it is necessary for the master to find
    out, which slaves are connected to the bus. This class provides the needed
    low level commands like get_long_acknowledge, get_short_acknowledge and
    get_negative_acknowledge.
    
    For more details please refer to the "Developers Manual, Data Transmission
    Protocol for IMPBUS2, 2008-11-18".
    """
    def __init__(self):
        Packet.__init__(self)
        Tables.__init__(self)
        
    def get_long_acknowledge(self,serno):
        """ GET LONG ACKNOWLEDGE
        
        This command with the number 2 will call up the slave which is
        addressed by its serial number. In return, the slave replies with
        a complete address block. It can be used to test the presence of
        a module in conjunction with the quality of the bus connection.
        
        >>> b = BaseCommands()
        >>> p = b.get_long_acknowledge(31001)
        >>> print p
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
        
        >>> b = BaseCommands()
        >>> p = b.get_short_acknowledge(31001)
        >>> print p
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
        
        >>> b = BaseCommands()
        >>> serno = int(0b111100000000000000000000)
        >>> p = b.get_acknowledge_for_serial_number_range(serno)
        >>> print p
        fd06000000f0d0
        """
        return self.pack(serno=range,cmd=0x06)
        
    def get_negative_acknowledge(self):
        """ GET NEGATIVE ACKNOWLEDGE
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        
        >>> b = BaseCommands()
        >>> p = b.get_negative_acknowledge()
        >>> print p
        fd0800ffffff60
        """
        return self.pack(serno=16777215,cmd=0x08)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
