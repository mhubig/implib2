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

from mock import call, MagicMock
from implib2.imp_modules import Module, ModuleError


# pylint: disable=invalid-name, protected-access
# pylint: disable=too-many-public-methods, attribute-defined-outside-init
class TestModule(object):
    def setup(self):
        self.serno = 31002
        self.bus = MagicMock()
        self.mod = Module(self.bus, self.serno)

    def test_get_table(self):
        with pytest.raises(ModuleError) as e:
            self.mod.get_table('ACTION_PARAMETER_TABLE')
        assert e.value.message == "Not yet implemented!"

    def test_get_serno(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        self.bus.get.return_value = (self.serno,)

        assert self.mod.get_serno() == self.serno
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_hw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'HWVersion'
        self.bus.get.return_value = (1.12176287368173,)

        assert self.mod.get_hw_version() == '1.12'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_fw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'FWVersion'
        self.bus.get.return_value = (1.11176287368173,)

        assert self.mod.get_fw_version() == '1.111763'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moist_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        self.bus.get.return_value = (50,)

        assert self.mod._get_moist_max_value() == 50
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moist_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        self.bus.get.return_value = (0,)

        assert self.mod._get_moist_min_value() == 0
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_temp_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        self.bus.get.return_value = (60,)

        assert self.mod._get_temp_max_value() == 60
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_temp_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        self.bus.get.return_value = (0,)

        assert self.mod._get_temp_min_value() == 0
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_NormalMeasure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x00,)

        assert self.mod.get_event_mode() == 'NormalMeasure'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_TRDScan(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x01,)

        assert self.mod.get_event_mode(), 'TRDScan'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_AnalogOut(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x02,)

        assert self.mod.get_event_mode() == 'AnalogOut'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_ACIC_TC(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x03,)

        assert self.mod.get_event_mode() == 'ACIC_TC'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_SelfTest(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x04,)

        assert self.mod.get_event_mode() == 'SelfTest'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_MatTempSensor(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x05,)

        assert self.mod.get_event_mode() == 'MatTempSensor'
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_UNKNOWN(self):
        self.bus.get.return_value = (0x06,)

        with pytest.raises(ModuleError) as e:
            self.mod.get_event_mode()
        assert e.value.message == "Unknown event mode!"

    def test_get_measure_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        self.bus.get.return_value = (0x00,)

        assert self.mod.get_measure_mode() == "ModeA"
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_measure_mode_UnknownMode(self):
        self.bus.get.return_value = (0x03,)
        with pytest.raises(ModuleError) as e:
            self.mod.get_measure_mode()
        assert e.value.message == "Unknown measure mode!"

    def test_unlock(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SupportPW'
        value = 66 + 0x8000
        self.bus.set.return_value = True

        assert self.mod.unlock()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_table(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        data = None

        with pytest.raises(ModuleError) as e:
            self.mod.set_table(table, data)
        assert e.value.message == "Not yet implemented!"

    def test_set_serno(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        value = self.serno + 1

        self.bus.set.return_value = True
        self.mod.unlock = MagicMock()

        assert self.mod.set_serno(value)
        assert self.mod._serno == value
        self.mod.unlock.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test__get_analog_output_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        mode = 0

        self.bus.get.return_value = (mode,)

        assert self.mod._get_analog_output_mode() == mode
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test__set_analog_output_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        value = 0

        self.bus.set.return_value = True

        assert self.mod._set_analog_output_mode(value)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test__set_analog_output_mode_WithWrongMode(self):
        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_output_mode(3)
        assert e.value.message == "Wrong AnalogOutputMode!"

    def test_set_analog_moist_ValueToLow(self):
        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_moist(-1)
        assert e.value.message == "Value out of range!"

    def test_set_analog_moist_ValueToHigh(self):
        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_moist(1001)
        assert e.value.message == "Value out of range!"

    def test_set_analog_moist_CouldNotSetEventMode(self):
        min_value = 0
        max_value = 25
        mvolt = 550

        self.mod._get_moist_min_value = MagicMock()
        self.mod._get_moist_min_value.return_value = min_value
        self.mod._get_moist_max_value = MagicMock()
        self.mod._get_moist_max_value.return_value = max_value
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False

        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_moist(mvolt)
        assert e.value.message == "Could not set event mode!"

    def test_set_analog_moist(self):
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'
        min_value = 0
        max_value = 25
        mvolt = 550
        value = (max_value - min_value) / 1000.0 * mvolt + min_value

        self.mod._get_moist_min_value = MagicMock()
        self.mod._get_moist_min_value.return_value = min_value
        self.mod._get_moist_max_value = MagicMock()
        self.mod._get_moist_max_value.return_value = max_value
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        assert self.mod._set_analog_moist(mvolt)
        self.mod._get_moist_min_value.assert_called_once_with()
        self.mod._get_moist_max_value.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("AnalogOut")
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_analog_temp_ValueToLow(self):
        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_temp(-1)
        assert e.value.message == "Value out of range!"

    def test_set_analog_temp_ValueToHigh(self):
        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_temp(1001)
        assert e.value.message == "Value out of range!"

    def test_set_analog_temp_CouldNotSetEventMode(self):
        min_value = -20
        max_value = 70
        mvolt = 550

        self.mod._get_temp_min_value = MagicMock()
        self.mod._get_temp_min_value.return_value = min_value
        self.mod._get_temp_max_value = MagicMock()
        self.mod._get_temp_max_value.return_value = max_value
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False

        with pytest.raises(ModuleError) as e:
            self.mod._set_analog_temp(mvolt)
        assert e.value.message == "Could not set event mode!"

    def test_set_analog_temp(self):
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'CompTemp'
        min_value = -20
        max_value = 70
        mvolt = 550
        value = (max_value - min_value) / 1000.0 * mvolt + min_value

        self.mod._get_temp_min_value = MagicMock()
        self.mod._get_temp_min_value.return_value = min_value
        self.mod._get_temp_max_value = MagicMock()
        self.mod._get_temp_max_value.return_value = max_value
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        assert self.mod._set_analog_temp(mvolt)
        self.mod._get_temp_min_value.assert_called_once_with()
        self.mod._get_temp_max_value.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("AnalogOut")
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_event_mode(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        event_modes = {
            "NormalMeasure":    0x00,
            "TRDScan":          0x01,
            "AnalogOut":        0x02,
            "ACIC_TC":          0x03,
            "SelfTest":         0x04,
            "MatTempSensor":    0x05}

        assert event_modes == self.mod.event_modes

        self.mod.unlock = MagicMock()

        expected_set_calles = []
        expected_unlock_calles = []
        for mode in event_modes:
            value = event_modes[mode]
            expected_set_calles.append(call(self.serno, table, param, [value]))
            expected_unlock_calles.append(call())
            assert self.mod.set_event_mode(mode)

        assert self.mod.unlock.call_args_list == expected_unlock_calles
        assert self.bus.set.call_args_list == expected_set_calles

    def test_set_event_mode_UnknownMode(self):
        mode = 'UNKNOWN'
        self.mod._unlocked = True
        with pytest.raises(ModuleError) as e:
            self.mod.set_event_mode(mode)
        assert e.value.message == "Invalid event mode!"

    def test_set_measure_mode_AlreadyInNormalMeasureMode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        mode = 'ModeA'

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"

        assert self.mod.set_measure_mode(mode)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_measure_mode_NotAlreadyInNormalMeasureMode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        mode = 'ModeA'

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"
        self.mod.set_event_mode = MagicMock()

        assert self.mod.set_measure_mode(mode)
        self.mod.set_event_mode.assert_called_once_with("NormalMeasure")
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_measure_mode_UnknownMode(self):
        with pytest.raises(ModuleError) as e:
            self.mod.set_measure_mode('ModeD')
        assert e.value.message == "Invalid measure mode!"

    def test_read_eeprom(self):
        with pytest.raises(NotImplementedError) as e:
            self.mod.read_eeprom()
        assert e.value.message == ""

    def test_write_eeprom(self):
        head = os.urandom(250)
        midl = os.urandom(250)
        tail = os.urandom(128)
        gen = (x for x in [head, midl, tail])

        eeprom = MagicMock()
        eeprom.__iter__.return_value = gen

        self.bus.set_eeprom_page.return_value = True
        self.mod.unlock = MagicMock()

        assert self.mod.write_eeprom(eeprom)
        self.mod.unlock.assert_called_once_with()
        expected = [call(self.serno, x, y) for x, y in
                    enumerate([head, midl, tail])]
        assert self.bus.set_eeprom_page.call_args_list == expected

    def test_write_eeprom_EEPROMWritingFailed(self):
        head = os.urandom(250)
        midl = os.urandom(250)
        tail = os.urandom(128)
        gen = (x for x in [head, midl, tail])

        eeprom = MagicMock()
        eeprom.__iter__.return_value = gen

        self.bus.set_eeprom_page.side_effect = [False]

        with pytest.raises(ModuleError) as e:
            self.mod.write_eeprom(eeprom)
        assert e.value.message == "Writing EEPROM failed!"

    def test_turn_asic_on(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SelfTest'
        value = [1, 1, 63, 0]

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        assert self.mod._turn_asic_on()
        self.mod.set_event_mode.assert_called_once_with(param)
        self.bus.set.assert_called_once_with(self.serno, table, param, value)

    def test_turn_asic_on_SetEventModeFailed(self):
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False

        with pytest.raises(ModuleError) as e:
            self.mod._turn_asic_on()
        assert e.value.message == "Could not set event mode!"

    def test_turn_asic_off(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SelfTest'
        value = [1, 0, 255, 0]

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        assert self.mod._turn_asic_off()
        self.mod.set_event_mode.assert_called_once_with(param)
        self.bus.set.assert_called_once_with(self.serno, table, param, value)

    def test_turn_asic_off_SetEventModeFailed(self):
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False

        with pytest.raises(ModuleError) as e:
            self.mod._turn_asic_off()
        assert e.value.message == "Could not set event mode!"

    def test_start_measure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 'ModeA'
        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"
        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = False
        self.bus.set.return_value = True

        assert self.mod.start_measure()
        self.mod.get_measure_mode.assert_called_once_with()
        self.mod.get_event_mode.assert_called_once_with()
        self.mod.measure_running.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_start_measure_MeasureModeNotA(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 'ModeB'
        self.mod.set_measure_mode = MagicMock()
        self.mod.set_measure_mode.return_value = True
        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"
        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = False
        self.bus.set.return_value = True

        assert self.mod.start_measure()
        self.mod.get_measure_mode.assert_called_once_with()
        self.mod.set_measure_mode.assert_called_once_with('ModeA')
        self.mod.get_event_mode.assert_called_once_with()
        self.mod.measure_running.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_start_measure_EventModeNotNormalMeasure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 'ModeA'
        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True
        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = False
        self.bus.set.return_value = True

        assert self.mod.start_measure()
        self.mod.get_measure_mode.assert_called_once_with()
        self.mod.get_event_mode.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("NormalMeasure")
        self.mod.measure_running.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_start_measure_ButMeasurementIsAlreadyStarted(self):
        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 'ModeA'
        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True
        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = True

        with pytest.raises(ModuleError) as e:
            self.mod.start_measure()
        assert e.value.message == "Measurement cycle already in progress!"

    def test_measure_running_YES(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'

        self.bus.get.return_value = (1,)

        assert self.mod.measure_running()
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_measure_running_Nop(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'

        self.bus.get.return_value = (0,)

        assert not self.mod.measure_running()
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_measure(self):
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'
        moist = 17.77

        self.bus.get.return_value = (moist,)

        assert self.mod.get_measure(quantity=param) == moist
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moisture(self):
        moist = 12.35

        self.mod.start_measure = MagicMock()
        self.mod.start_measure.return_value = True
        self.mod.measure_running = MagicMock()
        self.mod.measure_running.side_effect = (True, True, False)
        self.mod.get_measure = MagicMock()
        self.mod.get_measure.return_value = moist

        assert self.mod.get_moisture() == moist
        self.mod.start_measure.assert_called_once_with()
        assert (self.mod.measure_running.call_args_list ==
                [call(), call(), call()])
        self.mod.get_measure.assert_called_once_with(quantity='Moist')

    def test_get_transit_time_tdr_EventModeAlreadyNormalMeasure(self):
        transit_time = 123
        tdr_value = 321
        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        set_calls = [call(self.serno, table, param, [value])]

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1
        set_calls.append(call(self.serno, table, param, [value]))

        self.bus.set.return_value = True
        self.bus.get.side_effect = [(1,), (0,), (transit_time,), (tdr_value,)]

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 2
        set_calls.append(call(self.serno, table, param, [value]))

        assert self.mod._get_transit_time_tdr() == (transit_time, tdr_value)

        get_calls = [
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TransitTime'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TDRValue'),
        ]

        self.mod.get_event_mode.assert_called_once_with()
        assert self.bus.set.call_args_list == set_calls
        assert self.bus.get.call_args_list == get_calls

    def test_get_transit_time_tdr_EventModeNotAlreadyNormalMeasure(self):
        transit_time = 123
        tdr_value = 321
        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        set_calls = [call(self.serno, table, param, [value])]

        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1
        set_calls.append(call(self.serno, table, param, [value]))

        self.bus.set.return_value = True
        self.bus.get.side_effect = [(1,), (0,), (transit_time,), (tdr_value,)]

        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 2
        set_calls.append(call(self.serno, table, param, [value]))

        assert self.mod._get_transit_time_tdr() == (transit_time, tdr_value)

        get_calls = [
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TransitTime'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TDRValue'),
        ]

        self.mod.get_event_mode.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("NormalMeasure")
        assert self.bus.set.call_args_list == set_calls
        assert self.bus.get.call_args_list == get_calls

    def test__set_sdi12_address(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'ModuleInfo1'
        value = 0

        self.mod._set_sdi12_address(value)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test__set_sdi12_address_WrongAddress(self):
        with pytest.raises(ModuleError) as e:
            self.mod._set_sdi12_address(2000)
        assert e.value.message == 'SDI12 address out of range!'

    def test__set_protocol(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'Protocol'
        protocols = {'IMPBUS': 0, 'SDI12': 1}

        assert protocols == self.mod.protocols

        expected = []
        for protocol in protocols:
            value = protocols[protocol]
            self.mod._set_protocol(protocol)
            expected.append(call(self.serno, table, param, [value]))

        assert self.bus.set.call_args_list == expected

    def test__set_protocol_WrongProtocol(self):
        value = 'chocolate_jesus'
        with pytest.raises(ModuleError) as e:
            self.mod._set_protocol(value)
        assert e.value.message == "Wrong protocol: '{}'".format(value)
