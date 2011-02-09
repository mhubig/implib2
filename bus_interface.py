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

import time
from binascii import b2a_hex as b2a
from serialdevice import SerialDevice, SerialDeviceException 
from buscommands import BusCommands, BusCommandsException
from busresponce import BusResponce, BusResponceException

class IMPBusException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IMPBus(SerialDevice, BaseCommands, BaseResponce):
    """ 
    Class to combine the basic IMPBUS2 commands to higher level
    command cascades. Befor using any other command you first
    have to call init_bus() to get the device up and all modules
    talking at the same baudrate!
    
    >>> bus = IMPBus('loop://')
    >>> bus.DEBUG = True
    >>> bus.synchronise_bus()
    IMPBus instance initialized!
    """
    
    def __init__(self, port):
        self.DEBUG = False
        BaseCommands.__init__(self)
        BaseResponce.__init__(self)
        SerialDevice.__init__(self, port)
        if self.DEBUG == TRUE:
            print "IMPBus instance initialized!"
    
    def _divide_and_conquer(self, low, high, found):
        """ Recursiv divide-and-conquer algorythm to scan the IMPBUS.
        
        Divides the 24bit address range [0 - 16777215] in equal parts
        and uses the get_acknowledge_for_serial_number_range() methode
        to sort out the rages without a module. The found module serials
        are stored in the parameter list 'found'.
        """
        # if we have only one serial left check them direct.
        if high == low:
            if self.short_probe_module(high):
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
        
        >>> bus = IMPBus('/dev/tty.usbserial-A700eQFp')
        >>> bus.synchronise_bus()
        """
        
        table = 'SYSTEM_PARAMETER_TABLE'
        parameter = 'Baudrate'
        address = 16777215
        
        # trying to set baudrate at 1200
        self.ser.baudrate = 1200
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        self.close_device()
        
        # trying to set baudrate at 2400
        self.ser.baudrate = 2400
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        self.close_device()
        
        # trying to set baudrate at 4800
        self.ser.baudrate = 4800
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
        self.close_device()
        
        # trying to set baudrate at 9600
        self.ser.baudrate = 9600
        self.open_device()
        package = self.set_parameter(address, table, parameter, baudrate)
        bytes_send = self.write_package(package)
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
        found = list()
        self._divide_and_conquer(minserial, maxserial, found)
        return found
    
    def probe_module_long(self, serno):
        """ PROBE MODULE (LONGCOMMAND)
        
        This command with will call up the slave which is addressed
        by its serial number. In return, the slave replies with a
        complete address block. It can be used to test the presence
        of a module in conjunction with the quality of the bus connection.
        
        >>> bus = IMPBus('loop://')
        >>> bus.DEBUG = True
        >>> bus.probe_module_long(0)
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