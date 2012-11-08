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

class CommandError(Exception):
    pass

class Command(object):
    """ COMMANDS TO CONTROL A IMPBUS2.
    
    After building-up a IMP232N-bus, it is necessary for the master to find
    out, which slaves are connected to the bus. This class provides the needed
    low level commands like get_long_acknowledge, get_short_acknowledge and
    get_negative_acknowledge.
    
    COMMANDS TO CONTROL THE MODULES AND TRANSFER PARAMETERS
    
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
        self.tbl = Tables()
        self.pkg = Package()
        self.data_types = {
            0x00: '<{0}B', #  8-bit unsigned char
            0x01: '<{0}b', #  8-bit signed char
            0x02: '<{0}H', # 16-bit unsigned short
            0x03: '<{0}h', # 16-bit signed short
            0x04: '<{0}I', # 32-bit unsigned integer
            0x05: '<{0}i', # 32-bit signed integer
            0x06: '<{0}f', # 32-bit float
            0x07: '<{0}d'} # 64-bit double
        
    def get_long_ack(self, serno):
        """ GET LONG ACKNOWLEDGE
        
        This command with the number 2 will call up the slave which is
        addressed by its serial number. In return, the slave replies with
        a complete address block. It can be used to test the presence of
        a module in conjunction with the quality of the bus connection.
        
        >>> cmd = Command()
        >>> pkg = cmd.get_long_ack(31001)
        >>> b2a(pkg)
        'fd02001979007b'
        """
        return self.pkg.pack(serno=serno,cmd=0x02)
        
    def get_short_ack(self, serno):
        """ GET SHORT ACKNOWLEDGE
        
        This command will call up the slave which is addressed by its serial
        number. In return, the slave replies by just one byte: The CRC of it's
        serial number. It is the shortest possible command without the transfer
        of any data block and the only one without a complete address block. It
        can be used to test the presence of a module.
        
        >>> cmd = Command()
        >>> pkg = cmd.get_short_ack(31001)
        >>> b2a(pkg)
        'fd0400197900e7'
        """
        return self.pkg.pack(serno=serno, cmd=0x04)
        
    def get_range_ack(self, range):
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
        
        >>> cmd = Command()
        >>> rng = 0b111100000000000000000000
        >>> pkg = cmd.get_range_ack(rng)
        >>> b2a(pkg)
        'fd06000000f0d0'
        """
        return self.pkg.pack(serno=range,cmd=0x06)
        
    def get_negative_ack(self):
        """ GET NEGATIVE ACKNOWLEDGE
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        
        >>> cmd = Command()
        >>> pkg = cmd.get_negative_ack()
        >>> b2a(pkg)
        'fd0800ffffff60'
        """
        return self.pkg.pack(serno=16777215,cmd=0x08)
    
    def get_parameter(self, serno, table, param):
        """ COMMAND TO READ A PARAMETER.
        
        Command to read a parameter from one of the different
        parameter tables in the slave module.
        
        >>> cmd = Command()
        >>> pkg = cmd.get_parameter(31002,'SYSTEM_PARAMETER_TABLE','SerialNum')
        >>> b2a(pkg)
        'fd0a031a7900290100c4'
        """
        table = getattr(self.tbl, table)
        param = getattr(table, param)
        
        param_no = struct.pack('<B', param.No)
        param_ad = struct.pack('<B', 0)
        data = param_no + param_ad
        
        package = self.pkg.pack(serno=serno,cmd=table.Table.Get,data=data)
        return package
    
    def set_parameter(self, serno, table, param, ad_param, values):
        """ COMMAND TO SET A PARAMETER.
        
        Command to write a parameter to one of the different parameter
        tables in the slave module. It will checkt if the value has the
        right type and if this parameter is writable, according tho the
        tables.
        
        >>> cmd = Command()
        >>> pkg = cmd.set_parameter(31002,\
                'PROBE_CONFIGURATION_PARAMETER_TABLE',\
                'DeviceSerialNum', [31003])
        >>> b2a(pkg)
        'fd11071a79002b0c001b790000b0'
        """
        table  = getattr(self.tbl, table)
        param  = getattr(table, param)
        format = self.data_types[param.Type % 0x80]
        
        param_no = struct.pack('<B', param.No)
        param_ad = struct.pack('<B', ad_param)
        param = struct.pack(format.format(len(values)), *values)
        data = param_no + param_ad + param
        
        package = self.pkg.pack(serno=serno,cmd=table.Table.Set,data=data)
        return package
        
    def do_tdr_scan(self, serno, scan_start, scan_end, scan_span, scan_count):
        """ DO TDR SCAN
        
        Before using this command, the event TDRScan must be entered
        through setting the parameter Event in Action Parameter to 1.
        Then read the parameter again to see if the event has been
        successfully entered. If 0x81 (129) is returned, it is successful.
        This command may be carried out now. If 0x01 (1) is returned, this
        means that the event has not been entered. This should be checked
        until 0x81 is gotten.
        
        >>> cmd = Command()
        >>> pkg = cmd.do_tdr_scan(30001,1,126,2,64)
        >>> b2a(pkg)
        'fd1e06317500d3017e024000a4'
        """
        scan_start = struct.pack('<B', scan_start)
        scan_end   = struct.pack('<B', scan_end)
        scan_span  = struct.pack('<B', scan_span)
        scan_count = struct.pack('<H', scan_count)
        data = scan_start + scan_end + scan_span + scan_count
        
        package = self.pkg.pack(serno=serno,cmd=0x1e,data=data)
        return package
    
    def get_epr_image(self, serno, page_nr):
        """ VERY SPECIAL COMMAND TO GET ONE EEPROM PAGE.
        
        pagenr should be a string hex value!
        
        >>> cmd = Command()
        >>> pkg = cmd.get_epr_image(30001,0)
        >>> b2a(pkg)
        'fd3c0331750029ff0081'
        """
        param_no = struct.pack('<B', 255)
        param_ad = struct.pack('<B', page_nr)
        data = param_no + param_ad
        
        package = self.pkg.pack(serno=serno,cmd=0x3c,data=data)
        return package
    
    def set_epr_image(self, serno, page_nr, page):
        """ VERY SPECIAL COMMAND.
        
        pagenr should be a string hex value!
        
        >>> cmd  = Command()
        >>> page = [0,0,0,0,0,0,0,0,35,255,255,0]
        >>> pkg  = cmd.set_epr_image(30001,7,page)
        >>> b2a(pkg)
        'fd3d0f317500f6ff07000000000000000023ffff007b'
        """
        if len(page) > 250:
            raise ModuleCommandError("Page to big, exeeds 250 Bytes!")
        
        param_no = struct.pack('<B', 255)
        param_ad = struct.pack('<B', page_nr)
        param    = str()
        
        for byte in page:
            param += struct.pack('<B', byte)
        
        data = param_no + param_ad + param
        
        package = self.pkg.pack(serno=serno,cmd=0x3d,data=data)
        return package
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
