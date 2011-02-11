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
from module_commands import ModuleCommands, ModuleCommandsException
from module_responces import ModuleResponces, ModuleResponcesException
from imp_serialdevice import IMPSerialDeviceException

class ModuleException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Module(ModuleCommands, ModuleResponces):
    """ Class to combine the basic IMPBUS2 commands to
        higher level command cascades.
        
        Befor using any other command you first have to
        call init_bus() to get the device up and all modules
        talking at the same baudrate!
    
    >>> from bus_interface import IMPBus
    >>> bus = IMPBus('loop://')
    >>> module = Module(bus, serial)
    """
    
    def __init__(self, bus, serno):
        self.DEBUG = False
        self._serno = serno
        self._bus = bus
        ModuleCommands.__init__(self)
        ModuleResponces.__init__(self)
    
    #######################################
    # reading data from the module tables #
    #######################################
    
    def get_serial(self):
        try:
            if self.DEBUG: self._bus.DEBUG = True
            package = self.get_parameter(self._serno, 'SYSTEM_PARAMETER_TABLE', 'SerialNum')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
        except IMPSerialDeviceException as e:
            print e.value
            return None
        finally:
            if self.DEBUG:
                print 'Assembled package:', package
                print 'Bytes send:', bytes_send
                print 'Module Responce:', responce
        time.sleep(0.2)
        return responce
    
    def get_hw_version(self):
        try:
            if self.DEBUG: self._bus.DEBUG = True
            package = self.get_parameter(self._serno, 'SYSTEM_PARAMETER_TABLE', 'HWVersion')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
        except IMPSerialDeviceException as e:
            print e.value
            return None
        finally:
            if self.DEBUG:
                print 'Assembled package:', package
                print 'Bytes send:', bytes_send
                print 'Module Responce:', responce
        time.sleep(0.2)
        return responce
    
    def get_fw_version(self):
        try:
            if self.DEBUG: self._bus.DEBUG = True
            package = self.get_parameter(self._serno, 'SYSTEM_PARAMETER_TABLE', 'FWVersion')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
        except IMPSerialDeviceException as e:
            print e.value
            return None
        finally:
            if self.DEBUG:
                print 'Assembled package:', package
                print 'Bytes send:', bytes_send
                print 'Module Responce:', responce
        time.sleep(0.2)
        return responce

    def get_table(self, serno, table):
        try:
            if self.DEBUG: self._bus.DEBUG = True
            package = self.get_parameter(self._serno, table, 'GetData')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            if self.DEBUG:
                print 'Assembled package:', package
                print 'Bytes send:', bytes_send
                print 'Module Responce:', responce
        except IMPSerialDeviceException:
            return None
        time.sleep(0.2)
        return responce

    #################################
    # change the module settings    #  
    #################################

    def set_serial(self, serno):
        try:
            if self.DEBUG: self._bus.DEBUG = True            
            package = self.set_parameter(self._serno, 'SYSTEM_PARAMETER_TABLE', 'SerialNum', serno)
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            if self.DEBUG:
                print 'Assembled package:', package
                print 'Bytes send:', bytes_send
                print 'Module Responce:', responce
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()