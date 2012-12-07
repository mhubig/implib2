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
from mock import patch, Mock, MagicMock, call
from nose.tools import ok_, eq_, raises
from binascii import b2a_hex as b2a, a2b_hex as a2b

from implib2.imp_modules import Module, ModuleError

class TestModule(object):

    def setUp(self):
        self.serno = 31002
        self.bus = MagicMock()
        self.mod = Module(self.bus, self.serno)

    def tearDown(self):
        pass

    @raises(ModuleError)
    def test_get_table(self):
        self.mod.get_table('ACTION_PARAMETER_TABLE')

    def test_get_serial(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        self.bus.get.return_value = (self.serno,)
        eq_(self.mod.get_serial(), self.serno)
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
        eq_(self.mod.get_moist_max_value(), 50)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_moist_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        self.bus.get.return_value = (0,)
        eq_(self.mod.get_moist_min_value(), 0)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_temp_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        self.bus.get.return_value = (60,)
        eq_(self.mod.get_temp_max_value(), 60)
        self.bus.get.assert_called_once_with(self.serno, table, param)

    def test_get_temp_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        self.bus.get.return_value = (0,)
        eq_(self.mod.get_temp_min_value(), 0)
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

    def test_unlock(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'SupportPW'
        value = 66 + 0x8000
        self.bus.set.return_value = True
        ok_(self.mod._unlock())
        ok_(self.mod._unlocked)
        self.bus.set.assert_called_once_with(self.serno, table, param, [value])

    def test_read_eeprom(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'EPRByteLen'
        head = os.urandom(252)
        mid  = os.urandom(252)
        tail = os.urandom(128)
        pages = [head]
        pages.extend(30 * [mid])
        pages.extend([tail])

        self.bus.get.return_value = (252 * 31 + 128,)
        self.bus.get_epr_page.side_effect = pages

        self.mod._unlocked = True
        eeprom = self.mod.read_eeprom()

        self.bus.get.assert_called_once_with(self.serno, table, param)

        expected = [call(self.serno, x) for x in range(0,32)]
        eq_(self.bus.get_epr_page.call_args_list, expected)
        eq_(eeprom.get_page(0), head)
        eq_(eeprom.get_page(1), mid)
        eq_(eeprom.get_page(30), mid)
        eq_(eeprom.get_page(31), tail)

#    def test_write_eeprom(self):
#        epr_file = 'test.erp'
#        page_nr = 0
#        page = os.urandom(250)
#        gen = (x for x in [(page_nr, page)])
#
#        with patch('implib2.imp_eeprom.EEPRom') as mock:
#            eeprom = mock.return_value
#            eeprom.__iter__.return_value = gen
#            self.bus.set_eeprom_page.return_value = True
#            ok_(self.mod.write_eeprom(epr_file))
#
#        self.bus.set_eeprom_page.assert_called_once_with(self.serno,
#                page_nr, page)

