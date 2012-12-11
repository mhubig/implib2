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
import serial
from nose.tools import ok_, eq_, raises
from binascii import a2b_hex as a2b

from implib2.imp_device import Device, DeviceError

class TestPackage(object):
    # pylint: disable=C0103

    def setUp(self):
        self.mox = mox.Mox()
        self.ser = self.mox.CreateMock(serial.Serial)
        self.dev = Device(self.ser, '/dev/ttyS0')

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_open_device(self):
        self.ser.open()
        self.ser.flush()

        self.mox.ReplayAll()
        self.dev.open_device()
        self.mox.VerifyAll()

    def test_close_device_WhichIsOpen(self):
        self.ser.isOpen().AndReturn(True)
        self.ser.flush()
        self.ser.close()

        self.mox.ReplayAll()
        self.dev.close_device()
        self.mox.VerifyAll()

    def test_close_device_WhichIsClosed(self):
        self.ser.isOpen().AndReturn(False)

        self.mox.ReplayAll()
        self.dev.close_device()
        self.mox.VerifyAll()

    def test_write_pkg(self):
        packet = a2b('ffffff')
        self.ser.write(packet).AndReturn(3)

        self.mox.ReplayAll()
        ok_(self.dev.write_pkg(packet))
        self.mox.VerifyAll()

    @raises(DeviceError)
    def test_write_pkg_ButNotAllBytes(self):
        packet = a2b('ffffff')
        self.ser.write(packet).AndReturn(2)

        self.mox.ReplayAll()
        self.dev.write_pkg(packet)
        self.mox.VerifyAll()

    def test_read_pkg_OnlyHeader(self):
        pkg = a2b('fd0200bb81002d')

        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[0])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[1])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[2])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[3])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[4])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[5])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[6])

        self.mox.ReplayAll()
        eq_(self.dev.read_pkg(), pkg)
        self.mox.VerifyAll()

    @raises(DeviceError)
    def test_read_pkg_OnlyHeaderWithTimeout(self):
        self.ser.inWaiting().MultipleTimes().AndReturn(0)

        self.mox.ReplayAll()
        self.dev.TIMEOUT = 0.5
        self.dev.read_pkg()
        self.mox.VerifyAll()

    def test_read_pkg_HeaderAndData(self):
        pkg = a2b('000a05bb8100aa')
        dat = a2b('bb810000cc')

        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[0])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[1])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[2])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[3])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[4])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[5])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[6])

        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(dat[0])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(dat[1])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(dat[2])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(dat[3])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(dat[4])

        self.mox.ReplayAll()
        eq_(self.dev.read_pkg(), pkg + dat)
        self.mox.VerifyAll()

    @raises(DeviceError)
    def test_read_pkg_HeaderAndDataWithTimeout(self):
        pkg = a2b('000a05bb8100aa')

        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[0])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[1])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[2])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[3])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[4])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[5])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[6])

        self.ser.inWaiting().MultipleTimes().AndReturn(0)

        self.mox.ReplayAll()
        self.dev.TIMEOUT = 0.5
        self.dev.read_pkg()
        self.mox.VerifyAll()

    def test_read_bytes(self):
        pkg = a2b('ffff')

        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[0])
        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg[1])

        self.mox.ReplayAll()
        eq_(self.dev.read_bytes(2), pkg)
        self.mox.VerifyAll()

    @raises(DeviceError)
    def test_read_bytes_WithTimeout(self):
        self.ser.inWaiting().MultipleTimes().AndReturn(0)

        self.mox.ReplayAll()
        self.dev.TIMEOUT = 0.5
        self.dev.read_bytes(1)
        self.mox.VerifyAll()

    def test_read_something(self):
        pkg = a2b('ff')

        self.ser.inWaiting().AndReturn(1)
        self.ser.read().AndReturn(pkg)

        self.mox.ReplayAll()
        ok_(self.dev.read_something(), pkg)
        self.mox.VerifyAll()

    def test_read_something_ButGetNothing(self):
        self.ser.inWaiting().MultipleTimes().AndReturn(0)

        self.mox.ReplayAll()
        eq_(self.dev.read_something(), str())
        self.mox.VerifyAll()
