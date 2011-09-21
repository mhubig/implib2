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
from tools_crc import CRC, CRCError
from tools_eeprom import Parser, ParserError
from imp_serialdevice import SerialDeviceError
from module_commands import ModuleCommand, ModuleCommandError
from module_responces import ModuleResponce, ModuleResponceError

class ModuleError(Exception):
    pass

class Module(ModuleCommand, ModuleResponce):
    """ Class to combine the basic IMPBUS2 commands to
        higher level command cascades.
        
    >>> from bus_interface import IMPBus
    >>> bus = IMPBus('loop://')
    >>> modules = bus.scan_bus()
    >>> for module in modules:
    ...     modules.get_serial()
    """
    
    def __init__(self, bus, serno):
        super(Module, self).__init__()
        self.DEBUG     = False
        self._unlocked = False
        self._bus      = bus
        self._serno    = serno
        self._crc      = CRC()
        
        self.EVENT_MODES = {
            "NormalMeasure":    0x00,
            "TRDScan":          0x01,
            "AnalogOut":        0x02,
            "ACIC_TC":          0x03,
            "SelfTest":         0x04,
            "MatTempSensor":    0x05}
        
    def _get(self, table, param):
        """General get_parameter command"""
        if self.DEBUG: print("get_command: table={0} param={1}".format(table, param))
        try:
            package = self.get_parameter(self._serno, table, param)
            bytes_send = self._bus.write_package(package)
            responce = self.responce_get_parameter(self._bus.read_package(), table, param)
        except SerialDeviceException as e:
            raise ModuleException(e.message)
        time.sleep(0.2)
        return responce
    
    def _set(self, table, param, value):
        """General set_parameter command"""
        if self.DEBUG: print("set_command: table={0} param={1}".format(table, param))
        try:
            package = self.set_parameter(self._serno, table, param, value)
            bytes_send = self._bus.write_package(package)
            responce = self.responce_set_parameter(self._bus.read_package(), table)
        except SerialDeviceException as e:
            raise ModuleException(e.message)
        time.sleep(0.2)
        return responce
    
    def _unlock(self):
        if self.DEBUG: print("Unlocking Device")
        # Calculate the SupportPW: calc_crc(serno) + 0x8000
        passwd = self._reflect_bytes('%08x' % self._serno)
        passwd = self._crc.calc_crc(passwd)
        passwd = int(passwd, 16) + 0x8000
        
        # Unlock the device with the password
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SupportPW'
        value = passwd
        self._set(table, param, value)
        
        # Test is device is writeable
        table = 'PROBE_CONFIGURATION_PARAMETER_TABLE'
        param = 'ProbeType'
        value = 0xFF
        self._set(table, param, value)
        
        table = 'PROBE_CONFIGURATION_PARAMETER_TABLE'
        param = 'ProbeType' 
        
        if not self._get(table, param) == 255:
            raise ModuleException("Error: Couldn't unlock device!")
        
        self._unlocked = True
    
    #######################################
    # reading data from the module tables #
    #######################################
    
    def get_table(self, table):
        param = 'GetData'
        return self._get(table, param)
    
    def get_serial(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        return self._get(table, param)
    
    def get_hw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'HWVersion'
        return self._get(table, param)
    
    def get_fw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'FWVersion'
        return self._get(table, param)
    
    def get_moist_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        return self._get(table, param)
    
    def get_moist_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        return self._get(table, param)
    
    def get_temp_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        return self._get(table, param)
    
    def get_temp_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        return self._get(table, param)
    
    def get_event_mode(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        modes = {v:k for k, v in self.EVENT_MODES.items()}
        event = self._get(table, param)
        return modes[event % 0x80]
    
    def read_eeprom(self):
        eprimg = str()
        if not self._unlocked:
            self._unlock()        
        try:
            table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
            param = 'EPRByteLen'
            package = self.get_parameter(self._serno, table, param)
            bytes_send = self._bus.write_package(package)
            # TODO: test! -> is 'GetData' right?
            eprbytelen = self.responce_get_parameter(self._bus.read_package(), table, 'GetData')
            time.sleep(0.2)
        except SerialDeviceException as e:
            raise ModuleException(e.message)
        pages = eprbytelen / 252 + 1
        for page in range(0,pages):    
            try:
                package = self.get_epr_image(self._serno, page)
                bytes_send = self._bus.write_package(package)
                eprimg += self.responce_get_epr_image(self._bus.read_package())
                time.sleep(0.2)
            except SerialDeviceException as e:
                raise ModuleException(e.message)
        return eprimg
    
    ################################
    # change the module settings   #
    ################################
    
    def set_serial(self, serno):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        value = serno
        
        if not self._unlocked:
            self._unlock()
        state = self._set(table, param, value)
        self._serno = serno
        return state
    
    def set_analog_moist(self, mvolt=500):
        if not mvolt in range(0,1001):
            raise ModuleException('Value out of range!')
        
        min = self.get_moist_min_value()
        max = self.get_moist_max_value()
        value = (max - min) / 1000.0 * mvolt + min
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'
        print value
        if not self._unlocked:
            self._unlock()
        return self._set(table, param, value)
        
    def set_analog_temp(self, mvolt=500):
        if not mvolt in range(0,1001):
            raise ModuleException('Value out of range!')
        
        min = self.get_temp_min_value()
        max = self.get_temp_max_value()
        print "Min: {0}".format(min)
        print "Max: {0}".format(max)
        value = (max - min) / 1000.0 * mvolt + min
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'
        print "Calculated Value: {0}".format(value)
        if not self._unlocked:
            self._unlock()
        return self._set(table, param, value)
    
    def set_event_mode(self, event_mode="NormalMeasure"):
        """" Command to set the Event Mode of the probe.
        
        EventMode is used to control the slave to fulfil
        the different events.They are NormalMeasure, TDRScan,
        AnalogOut, ASIC_TC (Temperature Compensation),
        Self Test and MatTempSensor.
        """
        
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'
        try:
            value = self.EVENT_MODES[event_mode]
        except KeyError as e:
            raise ModuleException("'{0}' is not a valid EventMode!"
                .format(e.message))
        
        if not self._unlocked:
            self._unlock()
        return self._set(table, param, value)
        
    def write_eeprom(self, eeprom_file):
        if not self._unlocked:
            self._unlock()        
        eeprom = Parser(eeprom_file)
        for page_nr, page in eeprom:
            package = self.set_epr_image(self._serno, page_nr, page)
            try:
                bytes_send = self._bus.write_package(package)
                if not self.responce_set_erp_image(self._bus.read_package()):
                    raise ModuleException("Writing EEPROM Failed")
                time.sleep(0.2)
            except SerialDeviceException as e:
                raise ModuleException(e.message)
        return True

    #################################
    # perform measurment commands   #  
    #################################

    def do_measurement(self):
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
