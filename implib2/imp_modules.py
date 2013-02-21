#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2012, Markus Hubig <mhubig@imko.de>

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
from .imp_crc import MaximCRC
from .imp_eeprom import EEPRom


class ModuleError(Exception):
    pass


class Module(object):
    # pylint: disable=R0904
    """The Module object represents a IMPBus2 probe. It is used to provide a
    easy to use interface for the probe specific commands. It is mostly just a
    small wrapper around the much more general :func:`Bus.set` and
    :func:`Bus.get` commands. To create a `Module` object you first to supply
    a :class:`Bus` object and a serial number. As a quick example we will catch
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

        >>> module10.hw_version
        1.14
        >>> module10.fw_version
        1.140301
        >>> module11.hw_version
        1.14
        >>> module11.fw_version
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
        self._unlocked = False
        self._serno = serno

        self.event_modes = {
            "NormalMeasure":    0x00,
            "TRDScan":          0x01,
            "AnalogOut":        0x02,
            "ACIC_TC":          0x03,
            "SelfTest":         0x04,
            "MatTempSensor":    0x05}

        self.measure_modes = {
            "A": 0x00,
            "B": 0x01,
            "C": 0x02}

    ###########################
    ## Read only Properties  ##
    ###########################

    @property
    def serno(self):
        """The serial number of the module.

        :rtype: int

        """
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        return self.bus.get(self._serno, table, param)[param]

    @property
    def name(self):
        """The name of the module.

        :rtype: str

        """
        table = 'SYSTEM_PARAMETER'
        param = 'ModuleName'
        return self.bus.get(self._serno, table, param)[param].split('\x00')[0]

    @property
    def code(self):
        """The type code of the module.

        :rtype: str

        """
        table = 'SYSTEM_PARAMETER'
        param = 'ModuleCode'
        return self.bus.get(self._serno, table, param)[param]

    @property
    def info1(self):
        """Additional Info1 of the module.

        :rtype: str

        """
        table = 'SYSTEM_PARAMETER'
        param = 'Info1'
        return self.bus.get(self._serno, table, param)[param]

    @property
    def info2(self):
        """Additional Info2 of the module.

        :rtype: str

        """
        table = 'SYSTEM_PARAMETER'
        param = 'Info2'
        return self.bus.get(self._serno, table, param)[param]

    @property
    def hw_version(self):
        """The hardware version of the module.

        :rtype: str

        """
        table = 'SYSTEM_PARAMETER'
        param = 'HWVersion'
        return round(self.bus.get(self._serno, table, param)[param], 2)

    @property
    def fw_version(self):
        """The firmware version of the module.

        :rtype: str

        """
        table = 'SYSTEM_PARAMETER'
        param = 'FWVersion'
        return round(self.bus.get(self._serno, table, param)[param], 6)

    ###########################
    ## Writeable Properties  ##
    ###########################

    @property
    def measure_mode(self):
        """The measure mode of the probe. There a 3 different measure modes.

        .. note::
            **Mode A**
                On Request: The probe checks the parameter StartMeasure in
                Measure Parameter Table. If the parameter is 0, the probe does
                nothing. If the parameter is 1, the probe does the measurement
                and then sets the parameter to 0 again. Setting the parameter
                to 1 must be carried out through RS485 or IMPBus by an external
                command.

            **Mode B**
                Single: The probe measures once after it is powered on. This
                mode is normally used in the case that the probe is connected
                to a data logger which samples the analog output after being
                powered on. You can set a time (:attr:`measure_waitetime`) to
                wait befor starting the measurement.

            **Mode C**
                Cyclic: The probe measures cyclically. That means, the probe
                measures once and sleeps for some anount of time
                (:attr:`measure_sleeptime`) then it wakes up automatically and
                repeats the process. This mode is normally used in cases where
                the probe is always powered on.

        :param mode: 'A', 'B' or 'C'
        :type  mode: string
        :rtype: str
        :raises: **ModuleError** - If mode is unknown.

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MeasMode'
        modes = {v:k for k, v in self.measure_modes.items()}

        try:
            mode = modes[self.bus.get(self._serno, table, param)[param]]
        except KeyError:
            raise ModuleError("Unknown measure mode!")

        return mode

    @measure_mode.setter
    def measure_mode(self, mode='A'):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'

        try:
            value = self.measure_modes[mode]
        except KeyError as e:
            raise ModuleError(
                    "'{}' is not a valid measure mode!".format(e.message))

        if not self._get_event_mode() == "NormalMeasure":
            self._set_event_mode("NormalMeasure")

        assert self.bus.set(self._serno, table, param, {param: value})

    @property
    def measure_waittime(self):
        """ Wait time parameter for measurement mode B. See
        :attr:`measure_mode` for additional details.

        :param time: time in seconds (Default: 1)
        :type  mode: int
        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'WaitTimeInModeB'
        return self.bus.get(self._serno, table, param)[0]

    @measure_waittime.setter
    def measure_waittime(self, time=1):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'WaitTimeInModeB'
        value = time
        assert self.bus.set(self._serno, table, param, {param: value})

    @property
    def measure_sleeptime(self):
        """ Sleep time parameter for measurement mode C. See
        :attr:`measure_mode` for additional details.

        :param time: time in seconds (Default: 1)
        :type  mode: int
        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'SleepTimeInModeC'
        return self.bus.get(self._serno, table, param)[0]

    @measure_sleeptime.setter
    def measure_sleeptime(self, time):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'SleepTimeInModeC'
        value = [time]
        return self.bus.get(self._serno, table, param)[0]

    @property
    def analog_mode(self):
        """The analog output mode.

        This option, together with :attr:`moist_min`, :attr:`moist_max`,
        :attr:`temp_min`, :attr:`temp_max` and :func:`analog_mode` can be
        used to determine the mean of the analog moisture/temperatur output
        signal.

        | AnalogOutputMode 0: =>   0mV - 1000mV
        | AnalogOutputMode 1: => 200mV - 1000mV

        .. note::
            You can canculate the mean of the analog output signals like this:

            | AnalogOutputMode 0:
            |
            | temp_max - temp_min
            | ------------------- * [analog out in mV] = Measured Temperatur
            | 1000mV   -      0mV
            |
            |
            | AnalogOutputMode 1:
            |
            | temp_max - temp_min
            | ------------------- * [analog out in mV] = Measured Temperatur
            | 1000mV   -    200mV

        Analog output mode 1 is mainly intended to be used with an
        U/I-Converter.

        :param mode: 0 or 1
        :type  mode: int
        :rtype: int
        :raises: **ModuleError** - If mode is unknown.

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        return self.bus.get(self._serno, table, param)[0]

    @analog_mode.setter
    def analog_mode(self, mode=0):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'

        if not mode in (0, 1):
            raise ModuleError("Wrong analog mode!")

        value = mode

        assert self.bus.set(self._serno, table, param, [value])

    @property
    def moist_min(self):
        """The minimum moisture setting.

        This option set's the lower moisture border. Together with
        :attr:`moist_max` and :attr:`analog_mode` this setting can be
        used to determine the mean of the analog moisture output signal.
        For more information look at :attr:`analog_mode`.

        :param moist: minimum moisture value (Volumetric water content θ)
        :type  moist: int

        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        return self.bus.get(self._serno, table, param)[0]

    @moist_min.setter
    def moist_min(self, moist):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'

        if not moist in range(0,100):
            raise ModuleError("Maximum moisture value out of range")

        value = moist
        assert self.bus.set(self._serno, table, param, [value])

    @property
    def moist_max(self):
        """The maximum moisture setting.

        This option set's the upper moisture border. Together with
        :attr:`moist_min` and :attr:`analog_mode` this setting can be
        used to determine the mean of the analog moisture output signal.
        For more information look at :attr:`analog_mode`.

        :param moist: maximum moisture value (Volumetric water content θ)
        :type  moist: int
        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        return self.bus.get(self._serno, table, param)[0]

    @moist_max.setter
    def moist_max(self, moist):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'

        if not moist in range(0,100):
            raise ModuleError("Maximum moisture value out of range")

        value = moist
        assert self.bus.set(self._serno, table, param, [value])

    @property
    def temp_min(self):
        """The minimum temperature setting.

        This option set's the lower temperature border. Together with
        :attr:`temp_max` and :attr:`analog_mode` this setting can be
        used to determine the mean of the analog moisture output signal.
        For more information look at :attr:`analog_mode`.

        :param moist: minimum temperature value (C°)
        :type  moist: int
        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        return self.bus.get(self._serno, table, param)[0]

    @temp_min.setter
    def temp_min(self, moist):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'

        if not moist in range(-15, 50):
            raise ModuleError("Minimum temperatur value out of range")

        value = moist
        assert self.bus.set(self._serno, table, param, [value])

    @property
    def temp_max(self):
        """The minimum moisture setting.

        This option set's the upper temperature border. Together with
        :attr:`temp_min` and :attr:`analog_mode` this setting can be
        used to determine the mean of the analog moisture output signal.
        For more information look at :attr:`analog_mode`.

        :param moist: maximum temperature value (C°)
        :type  moist: int
        :rtype: int

        """
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        return self.bus.get(self._serno, table, param)[0]

    @temp_max.setter
    def temp_max(self, moist):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'

        if not moist in range(-15, 50):
            raise ModuleError("Maximum temperatur value out of range")

        value = moist
        assert self.bus.set(self._serno, table, param, [value])

    ###########################
    ## Functional Commands   ##
    ###########################

    def measure_start(self):
        """ Command to start a measurement cycle. 

        This command starts a measurement cycle. Or if there is
        already a measurement in progress just returns 'True'.

        :rtype: bool

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        if self.measure_running():
            return True

        # Refer to Protocol Handbook page 18.
        if not self.measure_mode == 'A':
            self.measure_mode = 'A'

        # Set Event mode to 'NormalMeasure'
        if not self._get_event_mode() == "NormalMeasure":
            assert self._set_event_mode("NormalMeasure")

        return self.bus.set(self._serno, table, param, [value])

    def measure_running(self):
        """This command checks if a measurement cycle is in progress.

        :rtype: bool

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        return self.bus.get(self._serno, table, param)[0] == 1

    def measure_data(self):
        """This command get's the measurement results.

        This command get's the whole tabel with the measurement results.

        :rtype: Table()

        """
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'GetData'
        return self.bus.get(self._serno, table, param)

    ###########################
    ##   Private Commands    ##
    ###########################

    @property
    def _event_mode(self):
        """ Event Mode Option.

        EventMode of the probe. This parameter can be set to six different
        values:

        .. note::
            0. *NormalMeasure:* Normal measurement Mode.
            1. *TDRScan:* TDRScan Mode.
            2. *AnalogOut:* Used for setting the analog out to a fixed value.
            3. *ASIC_TC:* Mode to perform a ASIC temperature compensation.
            4. *Self Test:* Mode to perform varios self tests.
            5. *MatTempSensor:* Mode to do a material temperatur compensation.

        :param mode: The EventMode to use.
        :type  mode: string
        :rtype: str
        :raises: **ModuleError** - If mode is not known.

        """
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        modes = {v:k for k, v in self.event_modes.items()}

        try:
            mode = modes[self.bus.get(self._serno, table, param)[param] % 0x80]
        except KeyError:
            raise ModuleError("Unknown event mode!")

        return mode

    @_event_mode.setter
    def _event_mode(self, mode="NormalMeasure"):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        try:
            value = self.event_modes[mode]
        except KeyError as e:
            raise ModuleError("Invalid event mode!")

        if not self._unlocked:
            self.unlock()

        return self.bus.set(self._serno, table, param, {param: value})


class SupportModule(Module):

    @property
    def serno(self):
        """The serial number of the module.

        :rtype: int

        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        return self.bus.get(self._serno, table, param)[0]

    @serno.setter
    def serno(self, value):
        """
        :param serno: Serial number so use.
        :type  serno: int
        """
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'

        if not self._unlocked:
            self.unlock()

        if self.bus.set(self._serno, table, param, [serno]):
            self._serno = serno
            self._unlocked = False
