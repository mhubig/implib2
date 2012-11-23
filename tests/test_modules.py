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

import mox
from nose.tools import ok_, eq_, raises
from binascii import b2a_hex as b2a, a2b_hex as a2b

from implib2.imp_bus import Bus, BusError
from implib2.imp_modules import Module, ModuleError

class TestModule(object):

    def setUp(self):
        self._serno = 31002
        self.mox = mox.Mox()
        self.bus = self.mox.CreateMock(Bus)
        self.mod = Module(self.bus, self._serno)

    def tearDown(self):
        self.mox.UnsetStubs()

    @raises(ModuleError)
    def test_get_table(self):
        self.mod.get_table('ACTION_PARAMETER_TABLE')

    def test_get_serial(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'
        self.bus.get(self._serno, table, param).AndReturn((31002,))

        self.mox.ReplayAll()
        eq_(self.mod.get_serial(), self._serno)
        self.mox.VerifyAll()

    def test_get_hw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'HWVersion'
        self.bus.get(self._serno, table, param).AndReturn((1.12176287368173,))

        self.mox.ReplayAll()
        eq_(self.mod.get_hw_version(), '1.12')
        self.mox.VerifyAll()

    def test_get_fw_version(self):
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'FWVersion'
        self.bus.get(self._serno, table, param).AndReturn((1.11176287368173,))

        self.mox.ReplayAll()
        eq_(self.mod.get_fw_version(), '1.111763')
        self.mox.VerifyAll()

    def test_get_moist_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMaxValue'
        self.bus.get(self._serno, table, param).AndReturn((50,))

        self.mox.ReplayAll()
        eq_(self.mod.get_moist_max_value(), 50)
        self.mox.VerifyAll()

    def test_get_moist_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'MoistMinValue'
        self.bus.get(self._serno, table, param).AndReturn((0,))

        self.mox.ReplayAll()
        eq_(self.mod.get_moist_min_value(), 0)
        self.mox.VerifyAll()

    def test_get_temp_max_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMaxValue'
        self.bus.get(self._serno, table, param).AndReturn((60,))

        self.mox.ReplayAll()
        eq_(self.mod.get_temp_max_value(), 60)
        self.mox.VerifyAll()

    def test_get_temp_min_value(self):
        table = 'DEVICE_CONFIGURATION_PARAMETER_TABLE'
        param = 'TempMinValue'
        self.bus.get(self._serno, table, param).AndReturn((0,))

        self.mox.ReplayAll()
        eq_(self.mod.get_temp_min_value(), 0)
        self.mox.VerifyAll()

    def test_get_event_mode_NormalMeasure(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x00,))
        self.mox.ReplayAll()
        eq_(self.mod.get_event_mode(), 'NormalMeasure')
        self.mox.VerifyAll()

    def test_get_event_mode_TRDScan(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x01,))
        self.mox.ReplayAll()
        eq_(self.mod.get_event_mode(), 'TRDScan')
        self.mox.VerifyAll()

    def test_get_event_mode_AnalogOut(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x02,))
        self.mox.ReplayAll()
        eq_(self.mod.get_event_mode(), 'AnalogOut')
        self.mox.VerifyAll()

    def test_get_event_mode_ACIC_TC(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x03,))
        self.mox.ReplayAll()
        eq_(self.mod.get_event_mode(), 'ACIC_TC')
        self.mox.VerifyAll()

    def test_get_event_mode_SelfTest(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x04,))
        self.mox.ReplayAll()
        eq_(self.mod.get_event_mode(), 'SelfTest')
        self.mox.VerifyAll()

    def test_get_event_mode_MatTempSensor(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x05,))
        self.mox.ReplayAll()
        eq_(self.mod.get_event_mode(), 'MatTempSensor')
        self.mox.VerifyAll()

    @raises(ModuleError)
    def test_get_event_mode_UNKNOWN(self):
        table = 'ACTION_PARAMETER_TABLE'
        param = 'Event'

        self.bus.get(self._serno, table, param).AndReturn((0x06,))
        self.mox.ReplayAll()
        self.mod.get_event_mode(), 'MatTempSensor'
        self.mox.VerifyAll()

