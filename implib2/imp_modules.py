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
import time, struct
from binascii import b2a_hex as b2a

import implib2

class ModuleError(Exception):
    pass

class Module(object):
    """ Class representing a IMPBus2 Module. """

    def __init__(self, bus, serno):
        self.crc = implib2.imp_crc.MaximCRC()
        self.bus = bus
        self._unlocked = False
        self._serno    = serno
        self.EVENT_MODES = {
            "NormalMeasure":    0x00,
            "TRDScan":          0x01,
            "AnalogOut":        0x02,
            "ACIC_TC":          0x03,
            "SelfTest":         0x04,
            "MatTempSensor":    0x05}

    def _unlock(self):
        # Calculate the SupportPW: calc_crc(serno) + 0x8000
        passwd = struct.pack('<I', self._serno)
        passwd = struct.unpack('<B', self.crc.calc_crc(passwd))[0] + 0x8000

        # Unlock the device with the password
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SupportPW'
        value = passwd

        self._unlocked = self.bus.set(self._serno, table, param, [value])
        return self._unlocked

    def get_table(self, table):
        """Spezial Command to get a whole table.

        **Not implemented yet!**

        Basicly you get a whole table, witch means the data-part of the
        recieved package consists of the concatinated table values. If
        the table don't fit into one package the status byte of the
        header-part will be '0xff'. Than you have to wait a bit and recieve
        packages as long as the status byte is '0x00' again. To extract the
        concatenated table-values you have to split the data in order of the
        Parameter-No., the length of each value can is equal to the
        Parameter-Length.

        You can use the parameters GetData, DataSize and TableSize to gain
        information about the spezific table.
        """
        raise ModuleError("Not yet implemented!")

    def get_serial(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        return self.bus.get(self._serno, table, param)[0]

    def get_hw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'HWVersion'
        return '{0:.2f}'.format(self.bus.get(self._serno, table, param)[0])

    def get_fw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'FWVersion'
        return '{0:.6f}'.format(self.bus.get(self._serno, table, param)[0])

    def get_moist_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        return self.bus.get(self._serno, table, param)[0]

    def get_moist_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        return self.bus.get(self._serno, table, param)[0]

    def get_temp_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        return self.bus.get(self._serno, table, param)[0]

    def get_temp_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        return self.bus.get(self._serno, table, param)[0]

    def get_event_mode(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        modes = {v:k for k, v in self.EVENT_MODES.items()}

        try:
            mode = modes[self.bus.get(self._serno, table, param)[0] % 0x80]
        except KeyError:
            raise ModuleError("Unknown event mode!")

        return mode

    def get_measure_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        return self.bus.get(self._serno, table, param)

    def read_eeprom(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'EPRByteLen'
        length = self.bus.get(self._serno, table, param)[0]

        if not self._unlocked:
            self._unlock()

        pages = length / 252
        if length % 252:
            pages += 1

        eeprom = implib2.imp_eeprom.EEPRom()
        for page in range(0, pages):
            eeprom.set_page(self.bus.get_epr_page(self._serno, page))
            time.sleep(0.2)

        if not eeprom.length == length:
            raise ModuleError("EEPRom length don't match!")
        return eeprom

    def set_table(self, table, data):
        """Spezial Command to set the values of a whole table.

        **Not implemented yet!**

        You can use the parameters GetData, DataSize and TableSize to gain
        information about the spezific table.
        """
        raise ModuleError("Not yet implemented!")

    def set_serno(self, serno):
        """Set the serialnumber of the module."""
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'

        if not self._unlocked:
            self._unlock()

        old_serno = self._serno
        self._serno = serno
        return self.bus.set(old_serno, table, param, [serno])

    def set_analog_moist(self, mvolt=500):
        if not mvolt in range(0,1001):
            raise ModuleError("Value out of range!")

        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'

        min = self.get_moist_min_value()
        max = self.get_moist_max_value()
        value = (max - min) / 1000.0 * mvolt + min

        if not self.set_event_mode("AnalogOut"): 
            raise ModuleError("Could not set event mode!")

        return self.bus.set(self._serno, table, param, [value])

    def set_analog_temp(self, mvolt=500):
        if not mvolt in range(0,1001):
            raise ModuleError('Value out of range!')

        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'

        min = self.get_temp_min_value()
        max = self.get_temp_max_value()
        value = (max - min) / 1000.0 * mvolt + min

        if not self.set_event_mode("AnalogOut"):
            raise ModuleError("Could not set event mode!")

        return self.bus.set(self._serno, table, param, [value])

    def set_event_mode(self, event_mode="NormalMeasure"):
        """" Command to set the Event Mode of the probe.

        EventMode is used to control the slave to fulfil
        the different events.They are NormalMeasure, TDRScan,
        AnalogOut, ASIC_TC (Temperature Compensation),
        Self Test and MatTempSensor.
        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        if not event_mode in self.EVENT_MODES:
            raise ModuleError("Invalid EventMode!")

        value = self.EVENT_MODES[event_mode]

        if not self._unlocked:
            self._unlock()

        return self.bus.set(self._serno, table, param, [value])

    def set_measure_mode(self, mode=0, default=False):
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'

        return self.bus.set(self._serno, table, param, [mode])

    def set_default_measure_mode(self, mode=2):
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'DefaultMeasMode'

        return self.bus.set(self._serno, table, param, [mode])

    def set_average_mode(self, mode=0):
        table = 'APPLICATION_PARAMETER_TABLE'
        param = 'AverageMode'
        return self.bus.set(self._serno, table, param, [mode])

    def write_eeprom(self, eprfile):
        eeprom = implib2.imp_eeprom.EEPRom()
        eeprom.read_ept(eprfile)

        if not self._unlocked:
            self._unlock()

        for page_nr, page in eeprom:
            if not self.bus.set_eeprom_page(self._serno, page_nr, page):
                raise ModuleError("Writing EEPRom failed!")
            time.sleep(0.05)

        return True

    def turn_ASIC_on(self):
        """" Command to start the selftest of the probe.

        SelfTest is used for primary for internal test by IMKO.
        In this context, it will be used to 'ON' the ASIC.
        """
        table    = 'ACTION_PARAMETER_TABLE'
        param    = 'SelfTest'
        value    = [1,1,63,0]

        if not self.set_event_mode("SelfTest"):
            raise ModuleError("Coul'd not set event mode!")

        return self.bus.set(self._serno, table, param, value)

    def turn_ASIC_off(self):
        """" Command to start the selftest of the probe.

        SelfTest is used for primary for internal test by IMKO.
        In this context, it will be used to 'OFF' the ASIC.
        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SelfTest'
        value = [1,0,255,0]

        if not self.set_event_mode("SelfTest"):
            raise ModuleError("Coul'd not set event mode!")

        return self.bus.set(self._serno, table, param, value)

    def get_measurement(self, type='Moist'):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        # Refer Protocol Handbook page 18.
        if not self.get_measure_mode() == 0:
            assert self.set_measure_mode(0)

        # set NormalMeasure
        if not self.get_event_mode() == "NormalMeasure":
            assert self.set_event_mode("NormalMeasure")

        assert self.bus.set(self._serno, table, param, [value])
        time.sleep(1.0)

        while self.bus.get(self._serno, table, param)[0]:
            time.sleep(0.5)

        table = 'MEASURE_PARAMETER_TABLE'
        param = type
        return self.bus.get(self._serno, table, param)[0]

    def get_moisture(self):
        return self.get_measurement(type='Moist')

    def get_transit_time_tdr(self):
        # ** Internal usage - Trime IBT
        if not self.get_event_mode() == "NormalMeasure":
            assert self.set_event_mode("NormalMeasure")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        assert self.bus.set(self._serno, table, param, [value])
        time.sleep(0.1)

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1
        assert self.bus.set(self._serno, table, param, [value])
        time.sleep(1.0)

        while self.bus.get(self._serno, table, param)[0]:
            time.sleep(0.5)

        table = 'MEASURE_PARAMETER_TABLE'
        param = 'TransitTime'
        transit_time = self.bus.get(self._serno, table, param)[0]

        param = 'TDRValue'
        tdr_value = self.bus.get(self._serno, table, param)[0]

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 2
        assert self.bus.set(self._serno, table, param, [value])
        time.sleep(0.1)

        return (transit_time, tdr_value)

