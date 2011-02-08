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
    
    COMMANDS TO CONTROL BUS AND TRANSFER PARAMETERS
    
    The main commands to transfer parameters are Get and Set Parameters.
    Get Parameters means information transport from slave to master and
    Set Parameters from master to slave.
    The parameters are divided in groups. There are different command
    numbers to get or set the parameters of a parameter group.
    
    +--------------------------+------------------+-------------------+
    | Parameter group:         |     Examples     |     Command no.   |
    |                          |                  |   Get   |   Set   |
    +--------------------------+------------------+---------+---------+
    | System parameters        | Baud rate        |   10    |   11    |
    +--------------------------+------------------+---------+---------+
    | Device configuration     | Measure cycle,   |   12    |   13    |
    | parameters               | Measurement rate |         |         |
    +--------------------------+------------------+---------+---------+
    | Device calibration       | ASIC TC,         |   14    |   15    |
    | parameters               | Electronic offset|         |         |
    +--------------------------+------------------+---------+---------+
    | Probe configuration      | TDR measure      |   16    |   17    |
    | prameters                | parameters       |         |         |
    +--------------------------+------------------+---------+---------+
    | Probe calibration        | Basic balancing, |   18    |   19    |
    | parameters               | Temp compensation|         |         |
    +--------------------------+------------------+---------+---------+
    | Action parameters        | SysErr, Event    |   20    |   21    |
    +--------------------------+------------------+---------+---------+
    | Measure parameters       | Count,t,tp,Ms    |   22    |   23    |
    +--------------------------+------------------+---------+---------+
    | Tp Moist parameters      | 101 points for   |   24    |   25    |
    |                          | calculating moist|         |         |
    +--------------------------+------------------+---------+---------+
    
    The parameters to be transferred by get or set commands are identified
    by a number, which is sent within the data block. There are special
    parameter as follows:
    
    +----------------+------------------------------------------------+
    | Parameter no.: | Explanation:                                   |
    +----------------+------------------------------------------------+
    | 0x01 ... 0xFA  | Ordinary number of the parameter to set or get |
    +----------------+------------------------------------------------+
    | 0xFB           | Configuration identification                   |
    +----------------+------------------------------------------------+
    | 0xFC           | The size of the parameter table                |
    +----------------+------------------------------------------------+
    | 0xFD           | Parameter table, infos about parameter group   |
    +----------------+------------------------------------------------+
    | 0xFE           | The data length of the parameter group         |
    +----------------+------------------------------------------------+
    | 0xFF           | Get all parameters of the parameter group      |
    +----------------+------------------------------------------------+
    
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
        
    def get_parameter(self,serno,table,param):
        """ COMMAND TO READ A PARAMETER.
        
        Command to read a parameter from one of the different
        parameter tables in the slave module.
        
        >>> b = BaseCommands()
        >>> p = b.get_parameter(31002,'SYSTEM_PARAMETER_TABLE','SerialNum')
        >>> print p
        fd0a031a7900290100c4
        """
        table = getattr(self, table)
        param = getattr(table, param)
        return self.pack(serno, table.Table.Get, param.No)
    
    def set_parameter(self,serno,table,param,value):
        """ COMMAND TO SET A PARAMETER.
        
        Command to write a parameter to one of the different parameter
        tables in the slave module. It will checkt if the value has the
        right type and if this parameter is writable, according tho the
        tables.
        
        TODO: Check the value type!
        
        >>> b = BaseCommands()
        >>> p = b.set_parameter(31002,'PROBE_CONFIGURATION_PARAMETER_TABLE',\
                                'DeviceSerialNum',31003)
        >>> print p
        fd11071a79002b0c000000791bc4
        """
        table = getattr(self, table)
        param = getattr(table, param)
        
        value = '%x' % value
        value = value.zfill(param.Length*2)
        
        if not param.writeable():
            raise BaseCommandsException('Parameter is not writeable!')
        
        if not len(value)/2 == param.Length:
            raise BaseCommandsException('Parameter has the wrong length!')
        
        return self.pack(serno, table.Table.Set, param.No, value)
        
    def do_tdr_scan(self,serno,start,end,span,count):
        """ DO TDR SCAN
        
        Before using this command, the event TDRScan must be entered
        through writing the parameter Event in Action Parameter to
        1.Then read the parameter again to see if the event has been
        successfully entered. If 0x81(129) is returned, it is successful.
        This command may be carried out now. If 0x01(1) is returned, this
        means that the event has not been entered. This should be checked
        until 0x81 is gotten.
        
        >>> b = BaseCommands()
        >>> p = b.do_tdr_scan(30001,1,126,2,64)
        >>> print p
        fd1e00317500da
        """
        start = "%02X" % start
        end = "%02X" % end
        span = "%02X" % span
        count = "%04X" % count
        param = start + end + span + count
        return self.pack(serno,0x1e,no_param=None,ad_param=None,param=param)
    
    def get_epr_image(self,serno,page_nr):
        """ VERY SPECIAL COMMAND.
        
        pagenr should be a string hex value!
        
        >>> b = BaseCommands()
        >>> p = b.get_epr_image(30001,7)
        >>> print p
        fd3c00317500a1
        """
        page_nr = '%02X' % page_nr
        param = 'FF' + page_nr
        return self.pack(serno,0x3c,no_param=None,ad_param=None,param=param)
    
    def set_epr_image(self,serno,page_nr,page):
        """ VERY SPECIAL COMMAND.
        
        pagenr should be a string hex value!
        
        >>> b = BaseCommands()
        >>> p = b.set_epr_image(30001,7,'FFFFFFFFFE000000')
        >>> print p
        fd3d003175006c
        """
        page_nr = '%02X' % page_nr
        param = 'FF' + page_nr + page
        return self.pack(serno,0x3d,no_param=None,ad_param=None,param=param)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
