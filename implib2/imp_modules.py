#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2013, Markus Hubig <mhubig@imko.de>

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
import struct
import string

from .imp_crc import MaximCRC


class ModuleError(Exception):
    pass


# pylint: disable=too-many-public-methods
class Module(object):
    """The Module object represents a IMPBus2 probe. It is used to provide a
    easy to use interface for the probe specific commands. It is mostly just a
    small wrapper around the much more general :func:`Bus.set` and
    :func:`Bus.get` commands. To create a `Module` object you first to supply a
    :class:`Bus` object and a serial number. As a quick example we will catch
    up with the code from :class:`Bus` and extend that a bit, pretending we
    have two probes with the serial numbers 10010 and 10011 connected to the
    bus::

        >>> from implib2 import Bus, Module
        >>> bus = Bus('/dev/ttyUSB0')
        >>> bus.sync()
        >>> bus.scan()
        (10010, 10011)

    Now that we found our two probes lets create the :class:`Module` objects::

        >>> module10 = Module(bus, 10010)
        >>> module11 = Module(bus, 10011)

    And now, lets use the :class:`Module` objects to gain some informations
    from the probes::

        >>> module10.get_hw_version()
        1.14
        >>> module10.get_fw_version()
        1.140301
        >>> module11.get_hw_version()
        1.14
        >>> module11.get_fw_version()
        1.140301

    :param bus: An instaciated :class:`Bus` object to use.
    :type  bus: :class:`Bus`

    :param serno: The serial number of the probe to address.
    :type  serno: int

    :rtype: :class:`Module`

    """
    def __init__(self, bus, serno):
        self.crc = MaximCRC()
        self.bus = bus
        self._serno = serno

        self.protocols = {
            'IMPBUS': 0,
            'SDI12':  1}

        self.event_modes = {
            "NormalMeasure":    0x00,
            "TRDScan":          0x01,
            "AnalogOut":        0x02,
            "ACIC_TC":          0x03,
            "SelfTest":         0x04,
            "MatTempSensor":    0x05}

        self.measure_modes = {
            "ModeA":            0x00,
            "ModeB":            0x01,
            "ModeC":            0x02}

        self.average_modes = {
            "CA":               0x00,
            "CK":               0x01,
            "CS":               0x02,
            "CF":               0x03}

    def unlock(self):
        """Command to unlock the write protected rows in the probes tables.
        The unlock key is the `CRC + 0x8000` of serial number of the probe.
        Be aware that the key changes as the serial number is changed.

        :rtype: bool

        """
        # Calculate the SupportPW: calc_crc(serno) + 0x8000
        passwd = struct.pack('<I', self._serno)
        passwd = struct.unpack('<B', self.crc.calc_crc(passwd))[0] + 0x8000

        # Unlock the device with the password
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SupportPW'
        value = passwd

        return self.bus.set(self._serno, table, param, [value])

    def get_event_mode(self):
        """Command to retrieve the event mode parameter of the probe. For more
        informations look at :func:`set_event_mode`.

        :raises : **ModuleError** - If event mode is not known.

        :rtype: string

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        modes = {v: k for k, v in self.event_modes.items()}

        mode = self.bus.get(self._serno, table, param)[0]
        if mode not in range(127, 134):
            raise ModuleError("Unknown event mode: %s" % mode)

        return modes[mode % 0x80]

    def set_event_mode(self, mode="NormalMeasure"):
        """Command to set the the EventMode of the probe. This parameter
        can be set to six different values:

        .. note::
            0. *NormalMeasure:* Normal measurement Mode.
            1. *TDRScan:* TDRScan Mode.
            2. *AnalogOut:* Used for setting the analog out to a fixed value.
            3. *ASIC_TC:* Mode to perform a ASIC temperature compensation.
            4. *Self Test:* Mode to perform varios self tests.
            5. *MatTempSensor:* Mode to do a material temperatur compensation.

        :param mode: The EventMode to use.
        :type  mode: string

        :rtype: bool

        :raises: **ModuleError** - If mode is not known.

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        if mode not in self.event_modes:
            raise ModuleError("%s: Invalid event mode!" % mode)

        value = self.event_modes[mode]

        self.unlock()
        self.bus.set(self._serno, table, param, [value])

        # let's try 5 times.
        for attempt in range(5):
            if self.bus.get(self._serno, table, param)[0] == value + 0x80:
                break
            if attempt == 4:
                raise ModuleError("Failed to set event mode!")

        return True

    def get_measure_mode(self):
        """Command to retrieve the measure mode parameter of the probe. For
        more informations look at :func:`set_measure_mode`.

        :raises: **ModuleError** - If measure mode is not known.

        :rtype: string

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        modes = {v: k for k, v in self.measure_modes.items()}

        try:
            mode = modes[self.bus.get(self._serno, table, param)[0]]
        except KeyError as err:
            raise ModuleError("Unknown measure mode: %s!" % err.args[0])

        return mode

    def set_measure_mode(self, mode='ModeA'):
        """Command to set the measure mode of the probe. There a 3 different
        measure modes.

        .. note::
            **ModeA**
                On Request, the probe checks the parameter StartMeasure in
                Measure Parameter Table. If the parameter is 0, the probe does
                nothing. If the parameter is 1, the probe does the measurement
                and then sets the parameter to 0 again. Setting the parameter
                to 1 must be carried out through RS485 or IMPBus by an external
                command.

            **ModeB**
                Single, the probe measures once after it is powered on. This
                mode is normally used in the case that the probe is connected
                to a data logger which samples the analog output after being
                powered on.

            **ModeC**
                Cyclic, the probe measures cyclically. That means, the probe
                measures once and sleeps the time SleepTimeInModeC, then it
                wakes up automatically and repeats the process. This mode is
                normally aused in casees when the probe is always powered and
                measures periodically.

        :param mode: Mode to use.
        :type  mode: string

        :rtype: bool

        :raises: **ModuleError** - If mode is unknown.

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'

        if mode not in self.measure_modes:
            raise ModuleError("%s: Invalid measure mode!" % mode)

        if not self.get_event_mode() == "NormalMeasure":
            raise ModuleError("Wrong event mode, need 'NormalMeasure'!")

        value = self.measure_modes[mode]

        return self.bus.set(self._serno, table, param, [value])

    def get_default_measure_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'DefaultMeasMode'
        modes = {v: k for k, v in self.measure_modes.items()}

        try:
            mode = modes[self.bus.get(self._serno, table, param)[0]]
        except KeyError as err:
            raise ModuleError("Unknown default measure mode: %s!" % err.args[0])

        return mode

    def set_default_measure_mode(self, mode='ModeC'):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'DefaultMeasMode'

        if mode not in self.measure_modes:
            raise ModuleError("%s: Invalid default measure mode!" % mode)

        if not self.get_event_mode() == "NormalMeasure":
            raise ModuleError("Wrong event mode, need 'NormalMeasure'!")

        value = self.measure_modes[mode]

        return self.bus.set(self._serno, table, param, [value])

    def get_average_mode(self):
        table = 'APPLICATION_PARAMETER_TABLE'
        param = 'AverageMode'
        modes = {v: k for k, v in self.average_modes.items()}

        try:
            mode = modes[self.bus.get(self._serno, table, param)[0]]
        except KeyError as err:
            raise ModuleError("Unknown average mode: %s!" % err.args[0])

        return mode

    def set_average_mode(self, mode='CA'):
        table = 'APPLICATION_PARAMETER_TABLE'
        param = 'AverageMode'

        if mode not in self.average_modes:
            raise ModuleError("%s: Invalid average mode!" % mode)

        value = self.average_modes[mode]
        return self.bus.set(self._serno, table, param, [value])

    def get_table(self, table):
        """Spezial Command to get a whole table.

        .. warning:: **Not yet implemented!**

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

        :param table: Table to retrieve from probe.
        :type  table: string

        :rtype: json

        """
        # pylint: disable=unused-argument, no-self-use
        raise NotImplementedError()

    def set_table(self, table, data):
        """Special command to set the values of a hole table.

        .. warning:: **Not yet implemented!**

        You can use the parameters GetData, DataSize and TableSize to gain
        information about the spezific table.

        :param table: Name of the table to write.
        :type  table: string

        :param data: Table data to write.
        :type  data: json

        :rtype: bool
        """
        # pylint: disable=unused-argument, no-self-use
        raise NotImplementedError()

    def get_serno(self):
        """Command to retrieve the serial number of the probe.

        :rtype: int

        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        return self.bus.get(self._serno, table, param)[0]

    def set_serno(self, serno):
        """Command to change the serial number of the probe.

        :param serno: Serial number so use.
        :type  serno: int

        :rtype: bool

        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'

        self.unlock()

        self.bus.set(self._serno, table, param, [serno])
        self._serno = serno
        return True

    def read_eeprom(self):
        """Command to read the EEPROM image from the probe. The image get's
        stored into a EEPROM object.

        :rtype: :class:`EEPROM`

        :raises: **ModuleError** - If length of the constructed :class:`EEPRom`
            does not match the length value from the probe table.

        """
        # pylint: disable=fixme
        # TODO: add methode to create a EEPROM file.
        raise NotImplementedError()

    def write_eeprom(self, image):
        """Command to write a new EEPROM image to the probe. The EEPROM
        image must be an instance of the :class:`EEPROM`.

        :param image: The Image to write.
        :type  image: :class:`EEPROM`

        :rtype: bool

        """
        self.unlock()

        for number, page in enumerate(image):
            if not self.bus.set_eeprom_page(self._serno, number, page):
                raise ModuleError("Writing EEPROM failed!")
            time.sleep(0.05)

        return True

    def get_hw_version(self):
        """Command to retrieve the hardware version number of the probe.

        :rtype: float

        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'HWVersion'
        return '{0:.2f}'.format(self.bus.get(self._serno, table, param)[0])

    def get_fw_version(self):
        """Command to retrieve the firmware version number of the probe.

        :rtype: float

        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'FWVersion'
        return '{0:.6f}'.format(self.bus.get(self._serno, table, param)[0])

    def start_measure(self):
        """This command starts a measurement cycle and returns when the
        measurement is finished. It's mostly used within a wrapper like
        :func:`get_moisture`.

        :rtype: bool

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        # Set Event mode to 'NormalMeasure'
        if not self.get_event_mode() == "NormalMeasure":
            raise ModuleError("Wrong event mode, need 'NormalMeasure'!")

        # Refer to Protocol Handbook page 18.
        if not self.get_measure_mode() == 'ModeA':
            raise ModuleError("Wrong measure mode, need 'ModeA'!")

        if self.measure_running():
            raise ModuleError("Measurement cycle already in progress!")

        return self.bus.set(self._serno, table, param, [value])

    def measure_running(self):
        """This command checks if the measurement cycle is in progress.

        :rtype: bool

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        return self.bus.get(self._serno, table, param)[0] == 1

    def get_measurement(self, quantity='Moist'):
        """This command gets the measured value of the requested quantity.
        It's mostly used within a wrapper like :func:`get_moisture`.

        :param quantity: The measure quantity to request.
        :type  quantity: str

        :rtype: int or float

        """
        table = 'MEASURE_PARAMETER_TABLE'
        param = quantity
        return self.bus.get(self._serno, table, param)[0]

    def get_moisture(self):
        """This command is a simple wrapper arrond :func:`start_measure`,
        :func:`measure_running` and :func:`get_measure`.

        :rtype: float

        """
        assert self.start_measure()
        while self.measure_running():
            time.sleep(0.500)
        return self.get_measurement(quantity='Moist')

    #########################
    # END of the Public API #
    #########################

    def _get_analog_output_mode(self):
        """Command to retrieve the analog output mode.

        This setting option, twogether with :func:`get_moist_min_value` and
        :func:`get_analog_output_mode` can be used to determine the mean of
        the analog moisture/temperatur output signal. For more information
        look at :func:`set_analog_output_mode`.

        .. note::
            | AnalogOutputMode 0: => 0.0V - 1.0V
            | AnalogOutputMode 1: => 0.2V - 1.0V

        Analog output mode 1 is mainly intended to be used with a
        U/I-Converter.

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        return self.bus.get(self._serno, table, param)[0]

    def _set_analog_output_mode(self, mode=0):
        """Command to set the analog output mode.

        This setting option, twogether with :func:`get_moist_min_value` and
        :func:`get_analog_output_mode` can be used to determine the mean of
        the analog moisture/temperatur output signal. For more information
        look at :func:`set_analog_output_mode`.

        .. note::
            | AnalogOutputMode 0: => 0.0V - 1.0V
            | AnalogOutputMode 1: => 0.2V - 1.0V

        Analog output mode 1 is mainly intended to be used with a
        U/I-Converter.

        :param:

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'

        if mode not in (0, 1):
            raise ModuleError("Wrong AnalogOutputMode!")

        value = mode

        return self.bus.set(self._serno, table, param, [value])

    def _get_moist_max_value(self):
        """Command to retrieve the maximum moisture setting.

        This setting option, twogether with :func:`get_moist_min_value` and
        :func:`get_analog_output_mode` can be used to determine the mean of
        the analog moisture output signal. For more information look at
        :func:`set_analog_output_mode`.

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        return self.bus.get(self._serno, table, param)[0]

    def _get_moist_min_value(self):
        """Command to retrieve the minimum moisture setting.

        This setting option, twogether with :func:`get_moist_max_value` and
        :func:`get_analog_output_mode` can be used to determine the mean of
        the analog moisture output signal. For more information look at
        :func:`set_analog_output_mode`.

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        return self.bus.get(self._serno, table, param)[0]

    def _get_temp_max_value(self):
        """Command to retrieve the maximum moisture setting.

        This setting option, twogether with :func:`get_temp_min_value` and
        :func:`get_analog_output_mode` can be used to determine the mean of
        the analog temperature output signal. For more information look at
        :func:`set_analog_output_mode`.

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        return self.bus.get(self._serno, table, param)[0]

    def _get_temp_min_value(self):
        """Command to retrieve the minimum moisture setting.

        This setting option, twogether with :func:`get_temp_max_value` and
        :func:`get_analog_output_mode` can be used to determine the mean of
        the analog temperature output signal. For more information look at
        :func:`set_analog_output_mode`.

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        return self.bus.get(self._serno, table, param)[0]

    def _set_analog_moist(self, mvolt=500):
        """Command so set the analog output of the moisture channel to a fixed
        value. This command can be used for calibration purposes.

        :param mvolt: Output current in millivolts (0-1000).
        :type  mbolt: int

        :rtype: bool

        :raises ModuleError: If `mvolt` parameter is out of range.
        :raises ModuleError: If EventMode can not be set to AnalogOut.

        """
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'

        if mvolt not in range(0, 1001):
            raise ModuleError("Value out of range!")

        if not self.get_event_mode() == "AnalogOut":
            raise ModuleError("Wrong event mode, need 'AnalogOut'!")

        if not self._get_analog_output_mode() == 0:
            raise ModuleError("Wrong AnalogOutputMode, need mode 0 here!")

        min_value = self._get_moist_min_value()
        max_value = self._get_moist_max_value()
        value = (max_value - min_value) / 1000.0 * mvolt + min_value

        return self.bus.set(self._serno, table, param, [value])

    def _get_analog_moist(self):
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'
        return self.bus.get(self._serno, table, param)[0]

    def _set_analog_temp(self, mvolt=500):
        """Command so set the analog output of the temperatur channel to a
        fixed value. This command can be used for calibration purposes.

        :param mvolt: Output current in millivolts (0-1000).
        :type  mbolt: int

        :rtype: bool

        :raises ModuleError: If `mvolt` parameter is out of range.
        :raises ModuleError: If EventMode can not be set to AnalogOut.

        """
        if mvolt not in range(0, 1001):
            raise ModuleError('Value out of range!')

        if not self.get_event_mode() == "AnalogOut":
            raise ModuleError("Wrong event mode, need 'AnalogOut'!")

        if not self._get_analog_output_mode() == 0:
            raise ModuleError("Wrong AnalogOutputMode, need mode 0 here")

        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'

        min_value = self._get_temp_min_value()
        max_value = self._get_temp_max_value()
        value = (max_value - min_value) / 1000.0 * mvolt + min_value

        return self.bus.set(self._serno, table, param, [value])

    def _get_analog_temp(self):
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'
        return self.bus.get(self._serno, table, param)[0]

    def _turn_asic_on(self):
        """Command to start the selftest of the probe.

        SelfTest is used for primary for internal test by IMKO.
        In this context, it will be used to 'ON' the ASIC.
        """

        if not self.get_event_mode() == "SelfTest":
            raise ModuleError("Wrong event mode, need 'SelfTest'!")

        table = 'ACTION_PARAMETER_TABLE'
        param = 'SelfTest'
        value = [1, 1, 63, 0]

        return self.bus.set(self._serno, table, param, value)

    def _turn_asic_off(self):
        """Command to start the selftest of the probe.

        SelfTest is used for primary for internal test by IMKO.
        In this context, it will be used to 'OFF' the ASIC.
        """

        if not self.get_event_mode() == "SelfTest":
            raise ModuleError("Wrong event mode, need 'SelfTest'!")

        table = 'ACTION_PARAMETER_TABLE'
        param = 'SelfTest'
        value = [1, 0, 255, 0]

        return self.bus.set(self._serno, table, param, value)

    def _get_transit_time_tdr(self):
        # ** Internal usage - Trime IBT
        if not self.get_event_mode() == "NormalMeasure":
            raise ModuleError("Wrong event mode, need 'NormalMeasure'!")

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        self.bus.set(self._serno, table, param, [value])

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1
        self.bus.set(self._serno, table, param, [value])

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
        self.bus.set(self._serno, table, param, [value])

        return (transit_time, tdr_value)

    def _set_sdi12_address(self, address=0):
        """Command to set the SDI-12 address

        This command sets the SDI-12 address of the probe.

        :param address: SDI-12 Address to set. (0-9, a-z, A-Z)
        :type  address: str

        :rtype: bool

        :raises ModuleError: If `address` parameter is out of range.

        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'ModuleInfo1'

        sdi12_address_rage = (range(0, 9) + [c for c in string.lowercase] +
                              [C for C in string.uppercase])

        if address not in sdi12_address_rage:
            raise ModuleError("SDI12 address out of range!")

        value = address

        return self.bus.set(self._serno, table, param, [value])

    def _set_protocol(self, protocol='IMPBUS'):
        """Command to set the bus protocol.

        :param protocol: Bus protocol to use. ('IMPBUS' or 'SDI12')
        :type  protocol: str

        :rtype: bool

        :raises ModuleError: If `protocol` parameter is unknown.
        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'Protocol'

        try:
            value = self.protocols[protocol]
        except KeyError as err:
            raise ModuleError("Wrong protocol: %s" % err.args[0])

        return self.bus.set(self._serno, table, param, [value])
