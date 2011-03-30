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
from tools_crc import CRC, CRCException
from tools_eeprom import Parser, ParserException
from imp_serialdevice import SerialDeviceException
from module_commands import ModuleCommands, ModuleCommandsException
from module_responces import ModuleResponces, ModuleResponcesException

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
        self.DEBUG = True
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
            responce = self.responce_set_parameter(self._bus.read_package())
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        
        time.sleep(0.2)
        
        try:
            package = self.set_parameter(self._serno,
                'PROBE_CONFIGURATION_PARAMETER_TABLE', 'ProbeType', 0xFF)
            self._bus.write_package(package)
            responce = self.responce_set_parameter(self._bus.read_package())
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        
        time.sleep(0.2)
          
        try:
            package = self.get_parameter(self._serno,
                'PROBE_CONFIGURATION_PARAMETER_TABLE', 'ProbeType')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'PROBE_CONFIGURATION_PARAMETER_TABLE', 'ProbeType')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        
        if not responce == 255:
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
            responce = self.responce_get_parameter(self._bus.read_package(),
                'SYSTEM_PARAMETER_TABLE', 'SerialNum')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return int(responce, 16)
    
    def get_hw_version(self):
        try:
            package = self.get_parameter(self._serno,
                'SYSTEM_PARAMETER_TABLE', 'HWVersion')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'SYSTEM_PARAMETER_TABLE', 'HWVersion')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce
    
    def get_fw_version(self):
        try:
            package = self.get_parameter(self._serno,
                'SYSTEM_PARAMETER_TABLE', 'FWVersion')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'SYSTEM_PARAMETER_TABLE', 'FWVersion')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_table(self, table):
        try:
            package = self.get_parameter(self._serno, table, 'GetData')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                table, 'GetData')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_eeprom(self):
        eprimg = str()
        if not self._unlocked:
            self._unlock()        
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'EPRByteLen')
            bytes_send = self._bus.write_package(package)
            eprbytelen = self.responce_get_parameter(self._bus.read_package(),
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'GetData')
            time.sleep(0.2)
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        pages = eprbytelen / 252 + 1
        for page in range(0,pages):    
            try:
                package = self.get_epr_image(self._serno, page)
                bytes_send = self._bus.write_package(package)
                eprimg += self.responce_get_epr_image(self._bus.read_package())
                time.sleep(0.2)
            except SerialDeviceException as e:
                raise ModuleException(e.value)
        return eprimg

    def get_moist_max_value(self):
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'MoistMaxValue')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'MoistMaxValue')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_moist_max_value(self):
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'MoistMaxValue')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'MoistMaxValue')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_moist_min_value(self):
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'MoistMinValue')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'MoistMinValue')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_temp_max_value(self):
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'TempMaxValue')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'TempMaxValue')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

    def get_temp_min_value(self):
        try:
            package = self.get_parameter(self._serno,
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'TempMinValue')
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(),
                'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'TempMinValue')
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        time.sleep(0.2)
        return responce

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
            responce = self.responce_set_parameter(self._bus.read_package())
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        self._serno = serno
        time.sleep(0.2)
        return responce
    
    def set_analog_moist(self, mvolt=500):
        if not volt in range(0,1000):
            raise ModuleException('Value out of range!')
        
        min = self.get_moist_max_value()
        max = self.get_moist_min_value()
        value = (abs(min) + abs(max)) / 1000 * mvolt
        
        if not self._unlocked:
            self._unlock()
        
        try:
            package = self.set_parameter(self._serno,
                'MEASURE_PARAMETER_TABLE', 'Moist', value)
            bytes_send = self._bus.write_package(package)
            responce = self.responce_set_parameter(self._bus.read_package())
        except SerialDeviceException as e:
            raise ModuleException(e.value)
        
        time.sleep(0.2)
        return responce
        
    def set_analog_temp(self, mvolt=500):
        if not volt in range(0,1000):
            raise ModuleException('Value out of range!')
        
        min = self.get_temp_max_value()
        max = self.get_temp_min_value()
        value = (abs(min) + abs(max)) / 1000 * mvolt
            
        if not self._unlocked:
            self._unlock()

        try:
            package = self.set_parameter(self._serno,
                'MEASURE_PARAMETER_TABLE', 'CompTemp', value)
            bytes_send = self._bus.write_package(package)
            responce = self.responce_set_parameter(self._bus.read_package())
        except SerialDeviceException as e:
            raise ModuleException(e.value)

        time.sleep(0.2)
        return responce
        
    def write_eeprom(self, eeprom_file):
        
        if not self._unlocked:
            self._unlock()
        
        eeprom = Parser(eeprom_file)
        for page_nr, page in eeprom:
            package = self.set_epr_image(self._serno, page_nr, page)
            try:
                bytes_send = self._bus.write_package(package)
                responce = self.responce_set_parameter(self._bus.read_package())
                time.sleep(0.2)
            except SerialDeviceException as e:
                raise ModuleException(e.value)
        return eeprom.length
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()