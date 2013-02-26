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

import os
import pytest
from mock import patch, call, MagicMock, PropertyMock
from implib2.imp_modules import Module, ModuleError


# pylint: disable=C0103,W0212,R0904,E1101,W0201
class TestModule(object):
    def setup(self):
        self.serno = 31002
        self.bus = MagicMock()
        self.mod = Module(self.bus, self.serno)

    ##############################
    ## Read only Property Tests ##
    ##############################

    def test_serno(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        value = self.serno

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.serno == value
        assert self.bus.get.mock_calls == expected

    def test_name(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'ModuleName'
        value = 'Trime Pico\x00\x00\x00\x00\x00\x00'

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.name == value.split('\x00')[0]
        assert self.bus.get.mock_calls == expected

    def test_code(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'ModuleCode'
        value = 100

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.code == value
        assert self.bus.get.mock_calls == expected

    def test_info1(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'Info1'
        value = 0

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.info1 == value
        assert self.bus.get.mock_calls == expected

    def test_info2(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'Info2'
        value = 1

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.info2 == value
        assert self.bus.get.mock_calls == expected

    def test_hw_version(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'HWVersion'
        value = 1.1399999856948853

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.hw_version == 1.14
        assert self.bus.get.mock_calls == expected

    def test_fw_version(self):
        serno = self.serno
        table = 'SYSTEM_PARAMETER'
        param = 'FWVersion'
        value = 1.14030300000000002

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.fw_version == 1.140303
        assert self.bus.get.mock_calls == expected

    ##############################
    ## Writeable Property Tests ##
    ##############################

    @pytest.mark.parametrize("mode", [(0, 'A'), (1, 'B'), (2, 'C')])
    def test_measure_mode_Get(self, mode):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MeasMode'
        value = mode[0]

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.measure_mode == mode[1]
        assert self.bus.get.mock_calls == expected

    def test_measure_mode_GetBadMode(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MeasMode'
        value = 3

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        with pytest.raises(ModuleError) as e:
            self.mod.measure_mode

        assert e.value.message == "Unknown measure mode!"
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("mode", [(0, 'A'), (1, 'B'), (2, 'C')])
    @patch('implib2.imp_modules.Module._event_mode', new_callable=PropertyMock)
    def test_measure_mode_Set(self, event_mode, mode):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MeasMode'
        value = mode[0]

        expected_bus = [call(serno, table, param, value)]
        expected_event = [call()]

        self.bus.set.return_value = True
        event_mode.return_value = "NormalMeasure"

        self.mod.measure_mode = mode[1]

        assert event_mode.mock_calls == expected_event
        assert self.bus.set.mock_calls == expected_bus

    @pytest.mark.parametrize("mode", [(0, 'A'), (1, 'B'), (2, 'C')])
    @patch('implib2.imp_modules.Module._event_mode', new_callable=PropertyMock)
    def test_measure_mode_SetWrongEventMode(self, event_mode, mode):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MeasMode'
        value = mode[0]

        expected_bus = [call(serno, table, param, value)]
        expected_event = [call(), call("NormalMeasure")]

        self.bus.set.return_value = True
        event_mode.return_value = "SelfTest"

        self.mod.measure_mode = mode[1]

        assert event_mode.mock_calls == expected_event
        assert self.bus.set.mock_calls == expected_bus

    def test_measure_mode_SetBadMode(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MeasMode'
        value = 'D'

        err_msg = "Not a valid measure mode: '{}'!".format(value)
        expected = []

        with pytest.raises(ModuleError) as e:
            self.mod.measure_mode = 'D'

        assert e.value.message == err_msg
        assert self.bus.set.mock_calls == expected

    def test_measure_waittime_Get(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'WaitTimeInModeB'
        value = 1.3

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.measure_waittime == value
        assert self.bus.get.mock_calls == expected

    def test_measure_waittime_Set(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'WaitTimeInModeB'
        value = 1.3

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.measure_waittime = value
        assert self.bus.set.mock_calls == expected

    def test_measure_sleeptime_Get(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'SleepTimeInModeC'
        value = 2.5

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.measure_sleeptime == value
        assert self.bus.get.mock_calls == expected

    def test_measure_sleeptime_Set(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'SleepTimeInModeC'
        value = 2.5

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.measure_sleeptime = value
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("mode", [0, 1])
    def test_analog_mode_get(self, mode):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'AnalogOutputMode'
        value = mode

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.analog_mode == value
        assert self.bus.get.mock_calls == expected

    def test_analog_mode_get_WrongMode(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'AnalogOutputMode'
        value = 3

        self.bus.get.return_value = value
        err_msg = "Got wrong analog mode!"
        expected = [call(serno, table, param)]

        with pytest.raises(ModuleError) as e:
            self.mod.analog_mode

        assert e.value.message == err_msg
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("mode", [0, 1])
    def test_analog_mode_set(self, mode):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'AnalogOutputMode'
        value = mode

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.analog_mode = value
        assert self.bus.set.mock_calls == expected

    def test_analog_mode_set_WrongMode(self):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'AnalogOutputMode'
        value = 3

        err_msg = "Wrong analog mode!"
        expected = []

        with pytest.raises(ModuleError) as e:
            self.mod.analog_mode = value

        assert e.value.message == err_msg
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("moist", xrange(0,101))
    def test_moist_min_Get(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMinValue'
        value = moist

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.moist_min == value
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("moist", [101, -1, 1000, -1000])
    def test_moist_min_GetOutOfRange(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMinValue'
        value = moist

        self.bus.get.return_value = value
        err_msg = "Minimum moisture value out of range"
        expected = [call(serno, table, param)]

        with pytest.raises(ModuleError) as e:
            self.mod.moist_min

        assert e.value.message == err_msg
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("moist", xrange(0,101))
    def test_moist_min_Set(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMinValue'
        value = moist

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.moist_min = value
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("moist", [101, -1, 1000, -1000])
    def test_moist_min_SetOutOfRange(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMinValue'
        value = moist

        self.bus.set.return_value = True
        err_msg = "Minimum moisture value out of range"
        expected = []

        with pytest.raises(ModuleError) as e:
            self.mod.moist_min = value

        assert e.value.message == err_msg
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("moist", xrange(0,101))
    def test_moist_max_Get(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMaxValue'
        value = moist

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.moist_max == value
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("moist", [101, -1, 1000, -1000])
    def test_moist_max_GetOutOfRange(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMaxValue'
        value = moist

        self.bus.get.return_value = value
        err_msg = "Maximum moisture value out of range"
        expected = [call(serno, table, param)]

        with pytest.raises(ModuleError) as e:
            self.mod.moist_max

        assert e.value.message == err_msg
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("moist", xrange(0,101))
    def test_moist_max_Set(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMaxValue'
        value = moist

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.moist_max = value
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("moist", [101, -1, 1000, -1000])
    def test_moist_max_SetOutOfRange(self, moist):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'MoistMaxValue'
        value = moist

        self.bus.set.return_value = True
        err_msg = "Maximum moisture value out of range"
        expected = []

        with pytest.raises(ModuleError) as e:
            self.mod.moist_max = value

        assert e.value.message == err_msg
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("temp", xrange(-15, 51))
    def test_temp_min_Get(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMinValue'
        value = temp

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.temp_min == value
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("temp", [-16, 51, -1000, 1000])
    def test_temp_min_GetOutOfRange(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMinValue'
        value = temp

        self.bus.get.return_value = value
        err_msg = "Minimum temperatur value out of range"
        expected = [call(serno, table, param)]

        with pytest.raises(ModuleError) as e:
            self.mod.temp_min

        assert e.value.message == err_msg
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("temp", xrange(-15, 51))
    def test_temp_min_Set(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMinValue'
        value = temp

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.temp_min = value
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("temp", [-16, 51, -1000, 1000])
    def test_temp_min_SetOutOfRange(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMinValue'
        value = temp

        self.bus.set.return_value = True
        err_msg = "Minimum temperatur value out of range"
        expected = []

        with pytest.raises(ModuleError) as e:
            self.mod.temp_min = value

        assert e.value.message == err_msg
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("temp", xrange(-15, 51))
    def test_temp_max_Get(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMaxValue'
        value = temp

        self.bus.get.return_value = value
        expected = [call(serno, table, param)]

        assert self.mod.temp_max == value
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("temp", [-16, 51, -1000, 1000])
    def test_temp_max_GetOutOfRange(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMaxValue'
        value = temp

        self.bus.get.return_value = value
        err_msg = "Maximum temperatur value out of range"
        expected = [call(serno, table, param)]

        with pytest.raises(ModuleError) as e:
            self.mod.temp_max

        assert e.value.message == err_msg
        assert self.bus.get.mock_calls == expected

    @pytest.mark.parametrize("temp", xrange(-15, 51))
    def test_temp_max_Set(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMaxValue'
        value = temp

        self.bus.set.return_value = True
        expected = [call(serno, table, param, value)]

        self.mod.temp_max = value
        assert self.bus.set.mock_calls == expected

    @pytest.mark.parametrize("temp", [-16, 51, -1000, 1000])
    def test_temp_max_SetOutOfRange(self, temp):
        serno = self.serno
        table = 'DEVICE_CONFIGURATION_PARAMETER'
        param = 'TempMaxValue'
        value = temp

        self.bus.set.return_value = True
        err_msg = "Maximum temperatur value out of range"
        expected = []

        with pytest.raises(ModuleError) as e:
            self.mod.temp_max = value

        assert e.value.message == err_msg
        assert self.bus.set.mock_calls == expected

    ##############################
    ## Functional Command Tests ##
    ##############################

    @patch('implib2.imp_modules.Module._event_mode',new_callable=PropertyMock)
    @patch('implib2.imp_modules.Module.measure_mode',new_callable=PropertyMock)
    @patch('implib2.imp_modules.Module.measure_running')
    def test_measure_start(self, measure_running, measure_mode, event_mode):
        serno = self.serno
        table = 'ACTION_PARAMETER'
        param = 'StartMeasure'
        value = 1

        expected = [call(serno, table, param, value)]

        measure_running.return_value = False
        measure_mode.return_value = 'A'
        event_mode.return_value = 'NormalMeasure'
        self.bus.set.return_value = True

        assert self.mod.measure_start()
        assert self.bus.set.mock_calls == expected
