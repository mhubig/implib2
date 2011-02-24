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
from tools_crc import CRC
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
        
    >>> from bus_interface import IMPBus
    >>> bus = IMPBus('loop://')
    >>> modules = bus.scan_bus()
    >>> for module in modules:
    ...     modules.get_serial()
    """
    
    def __init__(self, bus, serno):
        self.DEBUG = False
        self._unlocked = False
        self._bus = bus
        self._serno = serno
        self._crc = CRC()
        ModuleCommands.__init__(self)
        ModuleResponces.__init__(self)
    
    def _unlock(self):
        # Calculate the SupportPW: calc_crc(serno) + 0x8000
        passwd = self._reflect_bytes('%08x' % self._serno)
        passwd = self._crc.calc_crc(passwd)
        passwd = int(passwd, 16) + 0x8000
        if self.DEBUG: print 'Unlocking Device, with Password: %s' % hex(passwd)
        
        try:
            package = self.set_parameter(self._serno,
                'ACTION_PARAMETER_TABLE', 'SupportPW', passwd)
            self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_set_parameter(responce)
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        
        time.sleep(0.2)
        
        try:
            package = self.set_parameter(self._serno,
                'PROBE_CONFIGURATION_PARAMETER_TABLE', 'ProbeType', 0xFF)
            self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_set_parameter(responce)
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        
        time.sleep(0.2)
          
        try:
            package = self.get_parameter(self._serno,
                'PROBE_CONFIGURATION_PARAMETER_TABLE', 'ProbeType')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_get_parameter(responce,
                'PROBE_CONFIGURATION_PARAMETER_TABLE', 'ProbeType')
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        
        if not responce == 'ff':
            raise ModuleException("Error: Couldn't unlock device!")
        
        time.sleep(0.2)
        self._unlocked = True
    
    #######################################
    # reading data from the module tables #
    #######################################
    
    def get_serial(self):
        try:
            package = self.get_parameter(self._serno,
                'SYSTEM_PARAMETER_TABLE', 'SerialNum')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_get_parameter(responce,
                'SYSTEM_PARAMETER_TABLE', 'SerialNum')
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce
    
    def get_hw_version(self):
        try:
            package = self.get_parameter(self._serno,
                'SYSTEM_PARAMETER_TABLE', 'HWVersion')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_get_parameter(responce,
                'SYSTEM_PARAMETER_TABLE', 'HWVersion')
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce
    
    def get_fw_version(self):
        try:
            package = self.get_parameter(self._serno,
                'SYSTEM_PARAMETER_TABLE', 'FWVersion')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_get_parameter(responce,
                'SYSTEM_PARAMETER_TABLE', 'FWVersion')
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_table(self, table):
        try:
            package = self.get_parameter(self._serno, table, 'GetData')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            responce = self.responce_get_parameter(responce, table, 'GetData')
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_eeprom(self):
        if not self._unlocked:
            self._unlock()
            
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'EPRByteLen')
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
            eprbytelen = self.responce_get_parameter(responce,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'GetData')
            print eprbytelen
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        
        eprimg = ''
        pages = eprbytelen / 252 + 1
        for page in range(0,pages):    
            try:
                package = self.get_epr_image(self._serno, page)
                bytes_send = self._bus.write_package(package)
                responce = self._bus.read_package()
                eprimg += self.responce_get_epr_image(responce)
            except IMPSerialDeviceException as e:
                raise ModuleException(e.value)
                time.sleep(0.2)
        
        print len(eprimg) / 2
        return eprimg

    #################################
    # change the module settings    #  
    #################################

    def set_serial(self, serno):
        if not self._unlocked:
            self._unlock()
        try:
            package = self.set_parameter(self._serno,
                'SYSTEM_PARAMETER_TABLE', 'SerialNum', serno)
            bytes_send = self._bus.write_package(package)
            responce = self._bus.read_package()
        except IMPSerialDeviceException as e:
            raise ModuleException(e.value)
        self._serno = serno
        time.sleep(0.2)
        return responce
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()