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

import mox
from nose.tools import ok_, eq_, raises
from binascii import a2b_hex as a2b

from implib2.imp_bus import Bus, BusError
from implib2.imp_device import Device, DeviceError

class TestBus(object):
    # pylint: disable=C0103

    def setUp(self):
        self.mox = mox.Mox()
        self.dev = self.mox.CreateMock(Device)
        self.bus = Bus(self.dev)

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_synchronise_bus(self):
        baudrate = 9600

        self.dev.close_device()

        # baudrate at 1200
        self.dev.open_device(baudrate=1200)
        pkg = a2b('fd0b05ffffffaf0400600054')
        self.dev.write_pkg(pkg).AndReturn(12)
        self.dev.close_device()

        # baudrate at 2400
        self.dev.open_device(baudrate=2400)
        pkg = a2b('fd0b05ffffffaf0400600054')
        self.dev.write_pkg(pkg).AndReturn(12)
        self.dev.close_device()

        # baudrate at 4800
        self.dev.open_device(baudrate=4800)
        pkg = a2b('fd0b05ffffffaf0400600054')
        self.dev.write_pkg(pkg).AndReturn(12)
        self.dev.close_device()

        # baudrate at 9600
        self.dev.open_device(baudrate=9600)
        pkg = a2b('fd0b05ffffffaf0400600054')
        self.dev.write_pkg(pkg).AndReturn(12)
        self.dev.close_device()

        # open with 'baudrate'
        self.dev.open_device(baudrate=baudrate)

        self.mox.ReplayAll()
        self.bus.synchronise_bus(baudrate=baudrate)
        self.mox.VerifyAll()

    @raises(BusError)
    def test_synchronise_bus_WithWrongBaudrate(self):
        self.bus.synchronise_bus(baudrate=6666)

    def test_scan_bus(self):
        minserial = 0
        maxserial = 1

        pkg = a2b('fd06000100000f')
        res = a2b('ab')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_something().AndReturn(res)

        pkg = a2b('fd040000000027')
        res = a2b('')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_bytes(1).AndReturn(res)

        pkg = a2b('fd04000100008c')
        res = a2b('ab')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_bytes(1).AndReturn(res)

        self.mox.ReplayAll()
        eq_(self.bus.scan_bus(minserial, maxserial), (1,))
        self.mox.VerifyAll()

    def test_scan_bus_ButNothingFound(self):
        minserial = 0
        maxserial = 1

        pkg = a2b('fd06000100000f')
        res = a2b('')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_something().AndReturn(res)

        self.mox.ReplayAll()
        eq_(self.bus.scan_bus(minserial, maxserial), ())
        self.mox.VerifyAll()

    def test_find_single_module(self):
        pkg = a2b('fd0800ffffff60')
        res = a2b('000805ffffffd91a79000042')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndReturn(res)

        self.mox.ReplayAll()
        serno = self.bus.find_single_module()
        self.mox.VerifyAll()
        eq_(serno, (31002,))

    def test_find_single_module_FindNothing(self):
        pkg = a2b('fd0800ffffff60')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndRaise(DeviceError)

        self.mox.ReplayAll()
        serno = self.bus.find_single_module()
        self.mox.VerifyAll()
        eq_(serno, (False,))

    def test_probe_module_long(self):
        serno = 31002
        pkg = a2b('fd02001a79009f')
        res = a2b('0002001a7900a7')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndReturn(res)

        self.mox.ReplayAll()
        ok_(self.bus.probe_module_long(serno))
        self.mox.VerifyAll()

    def test_probe_module_long_ButGetDeviceError(self):
        serno = 31002
        pkg = a2b('fd02001a79009f')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndRaise(DeviceError)

        self.mox.ReplayAll()
        eq_(self.bus.probe_module_long(serno), (False,))
        self.mox.VerifyAll()

    def test_probe_module_short(self):
        serno = 31002
        pkg = a2b('fd04001a790003')
        res = a2b('24')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_bytes(1).AndReturn(res)

        self.mox.ReplayAll()
        ok_(self.bus.probe_module_short(serno))
        self.mox.VerifyAll()

    def test_probe_module_short_ButGetDeviceError(self):
        serno = 31002
        pkg = a2b('fd04001a790003')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_bytes(1).AndRaise(DeviceError)

        self.mox.ReplayAll()
        eq_(self.bus.probe_module_short(serno), (False,))
        self.mox.VerifyAll()

    def test_probe_range(self):
        rng = 0b111100000000000000000000
        pkg = a2b('fd06000000f0d0')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_something().AndReturn(a2b('ff'))

        self.mox.ReplayAll()
        ok_(self.bus.probe_range(rng))
        self.mox.VerifyAll()

    def test_probe_range_AndFindNothing(self):
        rng = 0b111100000000000000000000
        pkg = a2b('fd06000000f0d0')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_something().AndReturn(str())

        self.mox.ReplayAll()
        eq_(self.bus.probe_range(rng), False)
        self.mox.VerifyAll()

    def test_get(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'SerialNum'

        pkg = a2b('fd0a031a7900290100c4')
        res = a2b('000a051a7900181a79000042')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndReturn(res)

        self.mox.ReplayAll()
        eq_(self.bus.get(serno, table, param), (serno,))
        self.mox.VerifyAll()

    def test_set(self):
        serno = 31002
        table = 'PROBE_CONFIGURATION_PARAMETER_TABLE'
        param = 'DeviceSerialNum'
        value = [31003]

        pkg = a2b('fd11071a79002b0c001b790000b0')
        res = a2b('0011001a790095')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndReturn(res)

        self.mox.ReplayAll()
        eq_(self.bus.set(serno, table, param, value), True)
        self.mox.VerifyAll()

    def test_get_eeprom_page(self):
        serno = 30001
        page_nr = 0
        page = [17, 47, 196, 78, 55, 2, 243, 231, 251, 61]

        pkg = a2b('fd3c0331750029ff0081')
        res = a2b('003c0b1a790015112fc44e3702f3e7fb3dc5')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndReturn(res)

        self.mox.ReplayAll()
        eq_(self.bus.get_eeprom_page(serno, page_nr), page)
        self.mox.VerifyAll()

    def test_set_eeprom_page(self):
        serno = 30001
        page_nr = 7
        page = [0, 0, 0, 0, 0, 0, 0, 0, 35, 255, 255, 0]

        pkg = a2b('fd3d0f317500f6ff07000000000000000023ffff007b')
        res = a2b('003d001a79004c')
        self.dev.write_pkg(pkg).AndReturn(True)
        self.dev.read_pkg().AndReturn(res)

        self.mox.ReplayAll()
        ok_(self.bus.set_eeprom_page(serno, page_nr, page))
        self.mox.VerifyAll()

