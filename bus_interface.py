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

import time
from binascii import b2a_hex as b2a
from module_interface import Module, ModuleException
from bus_commands import BusCommands, BusCommandsException
from bus_responces import BusResponces, BusResponcesException
from imp_serialdevice import IMPSerialDevice, IMPSerialDeviceException 

class IMPBusException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IMPBus(IMPSerialDevice, BusCommands, BusResponces):
    """ 
    Class to combine the basic IMPBUS2 commands to higher level
    command cascades. Befor using any other command you first
    have to call init_bus() to get the device up and all modules
    talking at the same baudrate!
    
    >>> bus = IMPBus('loop://')
    >>> bus.DEBUG = True
    """
    
    def __init__(self, port):
        self.DEBUG = False
        self.bus_synced = False
        BusCommands.__init__(self)
        BusResponces.__init__(self)
        IMPSerialDevice.__init__(self, port)
    
    def _divide_and_conquer(self, low, high, found):
        """ Recursiv divide-and-conquer algorythm to scan the IMPBUS.
        
        Divides the 24bit address range [0 - 16777215] in equal parts
        and uses the get_acknowledge_for_serial_number_range() methode
        to sort out the rages without a module. The found module serials
        are stored in the parameter list 'found'.
        """
        # if we have only one serial left check them direct.
        if high == low:
            if self.probe_module_short(high):
                found.append(high)
                return True
            return False
        else:
            # calculate the broadcast address for range [low-high] and check
            # if there are some modules whithin the range, abort if not!
            broadcast = low + (high-low+1)/2
            if not self.probe_range(broadcast):
                return False
            
        # divide-and-conquer by splitting the range into two pices. 
        mid = (low + high)/2
        self._divide_and_conquer(low, mid, found)
        self._divide_and_conquer(mid+1, high, found)
        return True
    
    ####################################
    # Initialize the bus communication #
    ####################################
    
    def synchronise_bus(self, baudrate=9600):
        """ IMPBUS BAUDRATE SYNCHRONIZATION
        
        The communication between master and slaves can only be successful
        if they are on the same baud rate. In order to synchronise SM-modules
        on a given baud rate, the bus master has to transmit the broadcast 
        command "SetSysPara" with the parameter Baudrate on all possible baud
        rates (1200-2400-4800-9600). There must be a delay of at least 500ms
        after each command! The SM-modules understands one of these commands
        and will switch to the desired baud rate.
        
        >>> bus = IMPBus('loop://')
        >>> bus.DEBUG = True
        >>> bus.synchronise_bus(9600)
        Set baudrate with 1200baud!
        Set baudrate with 2400baud!
        Set baudrate with 4800baud!
        Set baudrate with 9600baud!
        """
        
        table = 'SYSTEM_PARAMETER_TABLE'
        parameter = 'Baudrate'
        address = 16777215
        
        # trying to set baudrate at 1200
        if self.DEBUG: print "Set baudrate with 1200baud!"
        self.ser.baudrate = 1200
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        self.close_device()
        
        # trying to set baudrate at 2400
        if self.DEBUG: print "Set baudrate with 2400baud!"
        self.ser.baudrate = 2400
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        self.close_device()
        
        # trying to set baudrate at 4800
        if self.DEBUG: print "Set baudrate with 4800baud!"
        self.ser.baudrate = 4800
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        self.close_device()
        
        # trying to set baudrate at 9600
        if self.DEBUG: print "Set baudrate with 9600baud!"
        self.ser.baudrate = 9600
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        
        self.bus_synced = True
        time.sleep(0.2)
    
    #############################
    # finding connected modules #
    #############################
    
    def scan_bus(self, minserial=0, maxserial=16777215):
        """ High level command to scan the IMPBUS for connected probes.
        
        This command is very similar to the short_probe_module()
        one. However, it addresses not just one single serial number,
        but a serial number range. This value of byte 4 to byte 6
        symbolizes a whole range.
        
        It's basiclly just a small wrapper for _divide_and_conquer().
        For details see the provided docstring of _divide_and_conquer.
        Usable like this:
        
        >>> bus = IMPBus('loop://')
        >>> bus.DEBUG = True
        >>> modules = bus.scan_bus(minserial=0, maxserial=2)
        """
        sernos = list()
        modules = list()
        self._divide_and_conquer(minserial, maxserial, sernos)
        
        if len(sernos) == 0:
            return modules
            
        for serno in sernos:
            modules.append(Module(self, serno))
        time.sleep(0.5)
        return modules
    
    def find_single_module(self):
        package = self.get_negative_acknowledge()
        bytes_send = self.write_package(package)
        bytes_recv = self.read_package()
        return self.responce_get_negative_acknowledge(bytes_recv)
    
    def probe_module_long(self, serno):
        """ PROBE MODULE (LONGCOMMAND)
        
        This command with will call up the slave which is addressed
        by its serial number. In return, the slave replies with a
        complete address block. It can be used to test the presence
        of a module in conjunction with the quality of the bus connection.
        
        >>> bus = IMPBus('loop://')
        >>> bus.DEBUG = True
        >>> bus.probe_module_long(0)
        0
        """
        package = self.get_long_acknowledge(serno)
        bytes_send = self.write_package(package)
        if self.DEBUG: print "Probing SerNo:", serno
        # Trying to get a respoce ...
        bytes_recv = self.read_package()
        if not bytes_recv:
            return False
        time.sleep(0.2)
        return self.responce_get_long_acknowledge(bytes_recv)
            
    def probe_module_short(self, serno):
        """ PROBE MODULE (SHORTCOMMAND)
        
        This command will call up the slave which is addressed
        by its serial number. In return, the slave replies by
        just one byte: The CRC of its serial number. It is the
        shortest possible command without the transfer of any
        data block and the only one without a complete address
        block. It can be used to test the presence of a module.
        
        >>> bus = IMPBus('loop://')
        >>> bus.DEBUG = True
        >>> bus.probe_module_short(0)
        >>> True
        """
        if self.DEBUG: print "Probing SerNo:", serno
        package = self.get_short_acknowledge(serno)
        serno = self._reflect_bytes('%06x' % serno)
        # send package
        bytes_send = self.write_package(package)
        # Trying to get a respoce ...
        responce = b2a(self.ser.read(1))
        if not self.check_crc(serno+responce):
            return False
        if self.DEBUG: print "---> Responce: %s" % responce 
        time.sleep(0.2)
        return True
        
    def probe_range(self, broadcast):
        """ PROBE ADDRESSRANGE
        
        This command is very similar to the previous one. However,
        it addresses not just one single serial number, but a serial
        number range. This value of byte 4 to byte 6 symbolizes a
        whole range according to a broacast pattern. For more details
        refer to the doctring of get_acknowledge_for_serial_number_range()
        or the the "Developers Manual, Data Transmission Protocol for
        IMPBUS2, 2008-11-18".
        
        >>> bus = IMPBus('loop://')
        >>> bus.DEBUG = True
        >>> bus.probe_range(16777215)
        Module seen at range 16777215
        True
        """
        package = self.get_acknowledge_for_serial_number_range(broadcast)
        bytes_send = self.write_package(package)
        if not self.read_something():
            if self.DEBUG: print "No Module seen at range %s" % broadcast
            return False
        if self.DEBUG: print "Module seen at range %s" % broadcast
        time.sleep(0.2)
        return True
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()