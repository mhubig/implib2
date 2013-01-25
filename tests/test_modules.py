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

import os
from mock import patch, call, MagicMock
from nose.tools import ok_, eq_, raises

from implib2.imp_modules import Module, ModuleError

class TestModule(object):
    # pylint: disable=C0103,W0212,R0904

    def setUp(self):
        self.serno = 31002
        self.bus = MagicMock()
        self.mod = Module(self.bus, self.serno)

    @raises(ModuleError)
    def test_get_table(self):
        self.mod.get_table('ACTION_PARAMETER_TABLE')

    def test_get_serno(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        self.bus.get.return_value = (self.serno,)
        eq_(self.mod.get_serno(), self.serno)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_hw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'HWVersion'
        self.bus.get.return_value = (1.12176287368173,)
        eq_(self.mod.get_hw_version(), '1.12')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_fw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'FWVersion'
        self.bus.get.return_value = (1.11176287368173,)
        eq_(self.mod.get_fw_version(), '1.111763')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moist_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        self.bus.get.return_value = (50,)
        eq_(self.mod._get_moist_max_value(), 50)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moist_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        self.bus.get.return_value = (0,)
        eq_(self.mod._get_moist_min_value(), 0)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_temp_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        self.bus.get.return_value = (60,)
        eq_(self.mod._get_temp_max_value(), 60)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_temp_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        self.bus.get.return_value = (0,)
        eq_(self.mod._get_temp_min_value(), 0)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_NormalMeasure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x00,)
        eq_(self.mod.get_event_mode(), 'NormalMeasure')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_TRDScan(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x01,)
        eq_(self.mod.get_event_mode(), 'TRDScan')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_AnalogOut(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x02,)
        eq_(self.mod.get_event_mode(), 'AnalogOut')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_ACIC_TC(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x03,)
        eq_(self.mod.get_event_mode(), 'ACIC_TC')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_SelfTest(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x04,)
        eq_(self.mod.get_event_mode(), 'SelfTest')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_event_mode_MatTempSensor(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x05,)
        eq_(self.mod.get_event_mode(), 'MatTempSensor')
        self.bus.get.assert_called_once_with(self.serno, table, param)

    @raises(ModuleError)
    def test_get_event_mode_UNKNOWN(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        self.bus.get.return_value = (0x06,)
        self.mod.get_event_mode()
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_measure_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        self.bus.get.return_value = (0x0,)
        self.mod.get_measure_mode()
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_unlock(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SupportPW'
        value = 66 + 0x8000
        self.bus.set.return_value = True
        ok_(self.mod.unlock())
        ok_(self.mod._unlocked)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_read_eeprom_ModuleAlreadyUnlocked(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'EPRByteLen'
        head = os.urandom(252)
        mid  = os.urandom(252)
        tail = os.urandom(128)
        length = (252 * 31 + 128)
        pages = [head]
        pages.extend(30 * [mid])
        pages.extend([tail])

        self.bus.get.return_value = (length,)
        self.bus.get_epr_page.side_effect = pages

        with patch('implib2.imp_modules.EEPRom') as mock:
            eeprom = mock()
            eeprom.length = length
            self.mod._unlocked = True
            eq_(self.mod.read_eeprom(), eeprom)
            expected = [call(x) for x in pages]
            eq_(eeprom.set_page.call_args_list, expected)

        self.bus.get.assert_called_once_with(self.serno, table, param)

        expected = [call(self.serno, x) for x in range(0, 32)]
        eq_(self.bus.get_epr_page.call_args_list, expected)

    def test_read_eeprom_ModuleNotAlreadyUnlocked(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'EPRByteLen'
        head = os.urandom(252)
        mid  = os.urandom(252)
        tail = os.urandom(128)
        length = (252 * 31 + 128)
        pages = [head]
        pages.extend(30 * [mid])
        pages.extend([tail])

        self.bus.get.return_value = (length,)
        self.bus.get_epr_page.side_effect = pages

        with patch('implib2.imp_modules.EEPRom') as mock:
            eeprom = mock()
            eeprom.length = length
            self.mod.unlock = MagicMock()
            self.mod._unlocked = False
            eq_(self.mod.read_eeprom(), eeprom)
            expected = [call(x) for x in pages]
            eq_(eeprom.set_page.call_args_list, expected)

        self.mod.unlock.assert_called_once_with()
        self.bus.get.assert_called_once_with(self.serno, table, param)

        expected = [call(self.serno, x) for x in range(0, 32)]
        eq_(self.bus.get_epr_page.call_args_list, expected)

    @raises(ModuleError)
    def test_read_eeprom_ButLengthDontMatch(self):
        length = (252 * 31 + 128)
        self.bus.get.return_value = (length,)

        with patch('implib2.imp_modules.EEPRom') as mock:
            eeprom = mock()
            eeprom.length = length - 1
            self.mod._unlocked = True
            self.mod.read_eeprom()

    @raises(ModuleError)
    def test_set_table(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        data = None
        self.mod.set_table(table, data)

    def test_set_serno_ModuleAlreadyUnlocked(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        value = self.serno + 1

        self.bus.set.return_value = True
        self.mod._unlocked = True

        ok_(self.mod.set_serno(value))

        eq_(self.mod._serno, value)
        eq_(self.mod._unlocked, False)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_serno_ModuleNotAlreadyUnlocked(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        value = self.serno + 1

        self.bus.set.return_value = True
        self.mod._unlocked = False
        self.mod.unlock = MagicMock()

        ok_(self.mod.set_serno(value))

        eq_(self.mod._serno, value)
        eq_(self.mod._unlocked, False)
        self.mod.unlock.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test__get_analog_output_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        mode  = 0

        self.bus.get.return_value = (mode,)

        eq_(self.mod._get_analog_output_mode(), mode)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test__set_analog_output_mode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        value = 0

        self.bus.set.return_value = True

        eq_(self.mod._set_analog_output_mode(value), True)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    @raises(ModuleError)
    def test__set_analog_output_mode_WithWrongMode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'AnalogOutputMode'
        value = 3
        self.mod._set_analog_output_mode(value)

    @raises(ModuleError)
    def test_set_analog_moist_ValueToLow(self):
        self.mod._set_analog_moist(-1)

    @raises(ModuleError)
    def test_set_analog_moist_ValueToHigh(self):
        self.mod._set_analog_moist(1001)

    @raises(ModuleError)
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

        self.mod._set_analog_moist(mvolt)

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

        self.mod._set_analog_moist(mvolt)
        self.mod._get_moist_min_value.assert_called_once_with()
        self.mod._get_moist_max_value.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("AnalogOut")
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    @raises(ModuleError)
    def test_set_analog_temp_ValueToLow(self):
        self.mod._set_analog_temp(-1)

    @raises(ModuleError)
    def test_set_analog_temp_ValueToHigh(self):
        self.mod._set_analog_temp(1001)

    @raises(ModuleError)
    def test_set_analog_temp_CouldNotSetEventMode(self):
        min_value = -20
        max_value =  70
        mvolt = 550

        self.mod._get_temp_min_value = MagicMock()
        self.mod._get_temp_min_value.return_value = min_value

        self.mod._get_temp_max_value = MagicMock()
        self.mod._get_temp_max_value.return_value = max_value

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False

        self.mod._set_analog_temp(mvolt)

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

        self.mod._set_analog_temp(mvolt)
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

        expected = []
        for mode in event_modes:
            value = event_modes[mode]
            expected.append(call(self.serno, table, param, [value]))
            self.mod._unlocked = True
            self.mod.set_event_mode(mode)

        eq_(self.bus.set.call_args_list, expected)

    def test_set_event_mode_NotAlreadyUnlocked(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'
        value = 0x00
        mode = "NormalMeasure"

        self.mod._unlocked = False
        self.mod.unlock = MagicMock()

        ok_(self.mod.set_event_mode(mode))
        self.mod.unlock.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    @raises(ModuleError)
    def test_set_event_mode_UnknownMode(self):
        mode = 'UNKNOWN'
        self.mod._unlocked = True
        self.mod.set_event_mode(mode)

    def test_set_measure_mode_AlreadyInNormalMeasureMode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        mode  = 'ModeA'

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"
        ok_(self.mod.set_measure_mode(mode))
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_set_measure_mode_NotAlreadyInNormalMeasureMode(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MeasMode'
        value = 0
        mode  = 'ModeA'

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"
        self.mod.set_event_mode = MagicMock()

        ok_(self.mod.set_measure_mode(mode))

        self.mod.set_event_mode.assert_called_once_with("NormalMeasure")
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_write_eeprom_ModuleAlreadyUnlocked(self):
        head = (0, os.urandom(252))
        mid  = (1, os.urandom(252))
        tail = (2, os.urandom(128))
        gen = (x for x in [head, mid, tail])

        eeprom = MagicMock()
        eeprom.__iter__.return_value = gen

        self.bus.set_eeprom_page.return_value = True
        self.mod._unlocked = True

        ok_(self.mod.write_eeprom(eeprom))

        expected = [call(self.serno, x[0], x[1]) for x in [head, mid, tail]]
        eq_(self.bus.set_eeprom_page.call_args_list, expected)

    def test_write_eeprom_ModuleNotAlreadyUnlocked(self):
        head = (0, os.urandom(252))
        mid  = (1, os.urandom(252))
        tail = (2, os.urandom(128))
        gen = (x for x in [head, mid, tail])

        eeprom = MagicMock()
        eeprom.__iter__.return_value = gen

        self.bus.set_eeprom_page.return_value = True
        self.mod._unlocked = False
        self.mod.unlock = MagicMock()

        ok_(self.mod.write_eeprom(eeprom))

        self.mod.unlock.assert_called_once_with()
        expected = [call(self.serno, x[0], x[1]) for x in [head, mid, tail]]
        eq_(self.bus.set_eeprom_page.call_args_list, expected)

    @raises(ModuleError)
    def test_write_eeprom_EEPRomWritingFailed(self):
        head = (0, os.urandom(252))
        mid  = (1, os.urandom(252))
        tail = (2, os.urandom(128))
        gen = (x for x in [head, mid, tail])

        eeprom = MagicMock()
        eeprom.__iter__.return_value = gen

        self.bus.set_eeprom_page.side_effect = [True, True, False]
        self.mod._unlocked = False
        self.mod.unlock = MagicMock()

        ok_(self.mod.write_eeprom(eeprom))

    def test_turn_asic_on(self):
        table    = 'ACTION_PARAMETER_TABLE'
        param    = 'SelfTest'
        value    = [1, 1, 63, 0]

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        ok_(self.mod._turn_asic_on())
        self.mod.set_event_mode.assert_called_once_with(param)
        self.bus.set.assert_called_once_with(self.serno, table, param, value)

    @raises(ModuleError)
    def test_turn_asic_on_SetEventModeFailed(self):
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False
        self.mod._turn_asic_on()

    def test_turn_asic_off(self):
        table    = 'ACTION_PARAMETER_TABLE'
        param    = 'SelfTest'
        value    = [1, 0, 255, 0]

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        ok_(self.mod._turn_asic_off())
        self.mod.set_event_mode.assert_called_once_with(param)
        self.bus.set.assert_called_once_with(self.serno, table, param, value)

    @raises(ModuleError)
    def test_turn_asic_off_SetEventModeFailed(self):
        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = False
        self.mod._turn_asic_off()

    def test_start_measure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 0x0

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"

        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = False

        self.bus.set.return_value = True

        eq_(self.mod.start_measure(), True)

        self.mod.get_measure_mode.assert_called_once_with()
        self.mod.get_event_mode.assert_called_once_with()
        self.mod.measure_running.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_start_measure_MeasureModeNotNull(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 0x1

        self.mod.set_measure_mode = MagicMock()
        self.mod.set_measure_mode.return_value = True

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NormalMeasure"

        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = False

        self.bus.set.return_value = True

        eq_(self.mod.start_measure(), True)

        self.mod.get_measure_mode.assert_called_once_with()
        self.mod.set_measure_mode.assert_called_once_with(0)
        self.mod.get_event_mode.assert_called_once_with()
        self.mod.measure_running.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_start_measure_EventModeNotNormalMeasure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 0x0

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = False

        self.bus.set.return_value = True

        eq_(self.mod.start_measure(), True)

        self.mod.get_measure_mode.assert_called_once_with()
        self.mod.get_event_mode.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("NormalMeasure")
        self.mod.measure_running.assert_called_once_with()
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    @raises(ModuleError)
    def test_start_measure_ButMeasurementIsAlreadyStarted(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'
        value = 1

        self.mod.get_measure_mode = MagicMock()
        self.mod.get_measure_mode.return_value = 0x0

        self.mod.get_event_mode = MagicMock()
        self.mod.get_event_mode.return_value = "NotNormalMeasure"

        self.mod.set_event_mode = MagicMock()
        self.mod.set_event_mode.return_value = True

        self.mod.measure_running = MagicMock()
        self.mod.measure_running.return_value = True

        self.mod.start_measure()

    def test_measure_running_YES(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'

        self.bus.get.return_value = (1,)

        eq_(self.mod.measure_running(), True)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_measure_running_Nop(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'StartMeasure'

        self.bus.get.return_value = (0,)

        eq_(self.mod.measure_running(), False)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_measure(self):
        table = 'MEASURE_PARAMETER_TABLE'
        param = 'Moist'
        moist = 17.77

        self.bus.get.return_value = (moist,)

        eq_(self.mod.get_measure(quantity=param), moist)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moisture(self):
        moist = 12.35

        self.mod.start_measure = MagicMock()
        self.mod.start_measure.return_value = True

        self.mod.measure_running = MagicMock()
        self.mod.measure_running.side_effect = (True, True, False)

        self.mod.get_value = MagicMock()
        self.mod.get_value.return_value = moist

        eq_(self.mod.get_moisture(), moist)
        self.mod.get_value.assert_called_once_with(quantity='Moist')
        eq_(self.mod.measure_running.call_args_list, [call(), call(), call()])
        self.mod.start_measure.assert_called_once_with()

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

        eq_(self.mod._get_transit_time_tdr(), (transit_time, tdr_value))

        get_calls = [
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TransitTime'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TDRValue'),
        ]

        self.mod.get_event_mode.assert_called_once_with()
        eq_(self.bus.set.call_args_list, set_calls)
        eq_(self.bus.get.call_args_list, get_calls)

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

        eq_(self.mod._get_transit_time_tdr(), (transit_time, tdr_value))

        get_calls = [
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'ACTION_PARAMETER_TABLE', 'StartMeasure'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TransitTime'),
            call(self.serno, 'MEASURE_PARAMETER_TABLE', 'TDRValue'),
        ]

        self.mod.get_event_mode.assert_called_once_with()
        self.mod.set_event_mode.assert_called_once_with("NormalMeasure")
        eq_(self.bus.set.call_args_list, set_calls)
        eq_(self.bus.get.call_args_list, get_calls)

