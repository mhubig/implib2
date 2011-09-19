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
#from binascii import b2a_hex as b2a
from module_interface import Module, ModuleException
from bus_commands import BusCommand, BusCommandError
from bus_responces import BusResponce, BusResponceError
from imp_serialdevice import SerialDevice, SerialDeviceEerror 

class IMPBusError(Exception):
    pass

class IMPBus(SerialDevice):
    """ 
    Class to combine the basic IMPBUS2 commands to higher level
    command cascades. Befor using any other command you first
    have to call init_bus() to get the device up and all modules
    talking at the same baudrate!
    
    >>> bus = IMPBus('loop://')
    >>> bus.DEBUG = True
    """
    
    def __init__(self, port):
        super(IMPBus, self).__init__(self)
        self.cmd = BusCommands()
        self.res = BusResponces()
        
        self.DEBUG = True
        self.bus_synced = False
    
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
        >>> bus.synchronise_bus(96)
        Set baudrate with 1200baud!
        Set baudrate with 2400baud!
        Set baudrate with 4800baud!
        Set baudrate with 9600baud!
        """
        
        address = 16777215
        table = 'SYSTEM_PARAMETER_TABLE'
        parameter = 'Baudrate'
        value = baudrate/100
        
        if not value in (12, 24, 48, 96):
            raise IMPBusException("Unknown baudrate!")
        
        # first close the device
        self.close_device()
        
        # trying to set baudrate at 1200
        if self.DEBUG:
            print "Set baudrate to {0} with 1200baud!".format(baudrate)
        self.open_device(baudrate=1200)
        package = self.cmd.set_parameter(address, table, parameter, value)
        bytes_send = self.write_package(package)
        time.sleep(0.5)
        self.close_device()
        
        # trying to set baudrate at 2400
        if self.DEBUG:
            print "Set baudrate to {0} with 2400baud!".format(baudrate)
        self.open_device(baudrate=2400)
        package = self.cmd.set_parameter(address, table, parameter, value)
        bytes_send = self.write_package(package)
        time.sleep(0.5)
        self.close_device()
        
        # trying to set baudrate at 4800
        if self.DEBUG:
            print "Set baudrate to {0} with 4800baud!".format(baudrate)
        self.open_device(baudrate=4800)
        package = self.cmd.set_parameter(address, table, parameter, value)
        bytes_send = self.write_package(package)
        time.sleep(0.5)
        self.close_device()
        
        # trying to set baudrate at 9600
        if self.DEBUG:
            print "Set baudrate to {0} with 9600baud!".format(baudrate)
        self.open_device(baudrate=9600)
        package = self.cmd.set_parameter(address, table, parameter, value)
        bytes_send = self.write_package(package)
        time.sleep(0.5)
        self.close_device()
        
        self.open_device(baudrate=baudrate)
        self.bus_synced = True
        if self.DEBUG:
            print "All modules synced to {0}baud!".format(baudrate)
        
        return True
    
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
        
        if self.DEBUG: print("Scanning bus for connected modules!")
        
        sernos = list()
        modules = list()
        self._divide_and_conquer(minserial, maxserial, sernos)
        
        if len(sernos) == 0:
            return modules
            
        for serno in sernos:
            if self.DEBUG:
                print("Found module with serno:{0}".format(serno))
            modules.append(Module(self, serno))
        
        return modules
    
    def find_single_module(self):
        package = self.cmd.get_negative_acknowledge()
        try:
            bytes_send = self.write_package(package)
            bytes_recv = self.read_package()
            return self.res.get_negative_acknowledge(bytes_recv)
        except SerialDeviceException, e:
            return False
    
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
        package = self.cmd.get_long_acknowledge(serno)
        bytes_send = self.write_package(package)
        if self.DEBUG: print "Probing SerNo:", serno
        # Trying to get a respoce ...
        bytes_recv = self.read_package()
        if not bytes_recv:
            return False
        time.sleep(0.2)
        return self.res.get_long_acknowledge(bytes_recv)
            
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
        package = self.cmd.get_short_ack(serno)
        serno = self._reflect_bytes('%06x' % serno)
        bytes_send = self.write_package(package)
        responce = self.read_bytes(1)
        if not self.res.get_short_ack(serno, responce):
            return False
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
        package = self.cmd.get_range_ack(broadcast)
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