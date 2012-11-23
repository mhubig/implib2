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

from imp_crc import MaximCRC, MaximCRCError
from imp_eeprom import EEPROM, EEPROMError

class ModuleError(Exception):
    pass

class Module(object):
    """ Class representing a IMPBus2 Module.

    Small example of how to use is together with the IMPBus class:
    """

    def __init__(self, bus, serno):
        self.crc = MaximCRC()
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
        self.bus.set(table, param, [value])

        self._unlocked = True

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
        param = 'GetData'
        raise ModuleError("Not yet implemented!")
        return False

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

    def read_eeprom(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'EPRByteLen'
        length = self.bus.get(self._serno, table, param)[0]

        if not self._unlocked:
            self._unlock()

        pages = length / 252
        if length % 252:
            pages += 1

        eprimg = list()
        for page in range(0, pages):
            package = self.cmd.get_epr_image(self._serno, page)
            bytes_recv = self.bus.talk(package)
            page = self.res.get_epr_image(bytes_recv)
            eprimg.extend(page)
            time.sleep(0.2)

        if not len(eprimg) == length:
            raise ModuleError("EEPROM length don't match!")
        return eprimg

    def set_table(self, table, data):
        """Spezial Command to set the values of a whole table.

        **Not implemented yet!**

        You can use the parameters GetData, DataSize and TableSize to gain
        information about the spezific table.
        """
        param = 'GetData'
        raise ModuleError("Not yet implemented!")
        return False

    def set_serial(self, serno):
        """Set the serialnumber of the module."""
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'

        if not self._unlocked:
            self._unlock()

        state = self.bus.set(table, param, [serno])
        self._serno = serno
        return state

    def set_analog_moist(self, mvolt=500):
        if not mvolt in range(0,1001):
            raise ModuleError("Value out of range!")

        min = self.get_moist_min_value()
        max = self.get_moist_max_value()
        value = (max - min) / 1000.0 * mvolt + min
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'

        if not self.set_event_mode("AnalogOut"): 
            raise ModuleError("Could not set event mode!")

        return self.bus.set(table, param, [value])

    def set_analog_temp(self, mvolt=500):
        if not mvolt in range(0,1001):
            raise ModuleError('Value out of range!')

        min = self.get_temp_min_value()
        max = self.get_temp_max_value()
        value = (max - min) / 1000.0 * mvolt + min
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'

        if not self.set_event_mode("AnalogOut"):
            raise ModuleError("Coul'd not set event mode!")

        return self.bus.set(table, param, [value])

    def set_event_mode(self, event_mode="NormalMeasure"):
        """" Command to set the Event Mode of the probe.

        EventMode is used to control the slave to fulfil
        the different events.They are NormalMeasure, TDRScan,
        AnalogOut, ASIC_TC (Temperature Compensation),
        Self Test and MatTempSensor.
        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        if event_mode in self.EVENT_MODES:
            value = self.EVENT_MODES[event_mode]
        else:
            raise ModuleError("Invalid EventMode!")

        if not self._unlocked:
            self._unlock()
        return self.bus.set(table, param, [value])

    def set_measmode(self,mode=0):
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        self.bus.set(table, param, [mode])
        time.sleep(0.1)
        return self.bus.set(table, param, [mode])

    def set_default_measmode(self,mode=2):
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'DefaultMeasMode'
        self.bus.set(table, param, [mode])
        time.sleep(0.1)
        return self.bus.set(table, param, [mode])

    def set_average_mode(self,mode=0):
        table = 'APPLICATION_PARAMETER_TABLE'
        param = 'AverageMode'
        self.bus.set(table, param, [mode])
        time.sleep(0.1)
        return self.bus.set(table, param, [mode])

    def write_eeprom(self, eeprom_file):
        eeprom = EEPROM(eeprom_file)

        if not self._unlocked:
            self._unlock()

        for page_nr, page in eeprom:
            package = self.cmd.set_epr_image(self._serno, page_nr, page)
            bytes_recv = self.bus.talk(package)
            responce = self.res.set_epr_image(bytes_recv)
            if not self.res.set_epr_image(bytes_recv):
                raise ModuleError("Writing EEPROM Failed")
            time.sleep(0.2)
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

        return self.bus.set(table, param, value)

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

        return self.bus.set(table, param, value)

    def get_moisture(self):

        # set MeasMode ModeA
        # Refer Protocol Handbook page 18.
        self.set_measmode(mode=0)

        # set NormalMeasure
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        self.bus.set(table, param, [1])
        time.sleep(1.0)

        while self.bus.get(table, param)[0]:
            time.sleep(0.5)

        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'
        return self.bus.get(table, param)[0]

    def get_measure(self,strName):

        if strName == 'RbC': strName = 'Info1'

        # set MeasMode ModeA
        # Refer Protocol Handbook page 18.
        self.set_measmode(mode=0)

        # set NormalMeasure
        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        self.bus.set(table, param, [1])
        time.sleep(1.0)

        while self.bus.get(table, param)[0]:
            time.sleep(0.5)

        table = 'MEASURE_PARAMETER_TABLE'
        param = strName
        return self.bus.get(table, param)[0]

    def get_transit_time_tdr(self):
        # ** Internal usage - Trime IBT

        if not self.get_event_mode() == "NormalMeasure":
            self.set_event_mode("NormalMeasure")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        self.bus.set(table, param, [0])
        time.sleep(0.1)

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        self.bus.set(table, param, [1])
        time.sleep(1.0)

        while self.bus.get(table, param)[0]:
            time.sleep(0.5)

        table = 'MEASURE_PARAMETER_TABLE'
        param = 'TransitTime'
        tt = self.bus.get(table, param)[0]

        param = 'TDRValue'
        tdr = self.bus.get(table, param)[0]

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        self.bus.set(table, param, [2])
        time.sleep(0.1)

        return tt, tdr

