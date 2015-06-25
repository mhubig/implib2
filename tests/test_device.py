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
import pytest
import serial  # noqa pylint: disable=W0611
from mock import patch, call
from binascii import a2b_hex as a2b
from implib2.imp_device import Device, DeviceError


# pylint: disable=C0103,E1101,W0201
class TestPackage(object):

    def setup(self):
        with patch('serial.Serial') as mock:
            self.ser = mock()
            self.dev = Device('/dev/ttyS0')

    def test_open_device(self):
        self.dev.open_device()
        expected = [call(), call()]
        assert self.ser.open.call_args_list == expected
        assert self.ser.flush.call_args_list == expected

    def test_close_device_WhichIsOpen(self):
        self.ser.isOpen.return_value = True
        self.dev.close_device()
        self.ser.isOpen.assert_called_once_with()
        expected = [call(), call()]
        assert self.ser.flush.call_args_list == expected
        self.ser.close.assert_called_once_with()

    def test_close_device_WhichIsClosed(self):
        self.ser.isOpen.return_value = False
        self.dev.close_device()
        self.ser.isOpen.assert_called_once_with()

    def test_write_pkg(self):
        packet = a2b('ffffff')
        self.ser.write.return_value = 3
        assert self.dev.write_pkg(packet)
        self.ser.write.assert_called_once_with(packet)

    def test_write_pkg_ButNotAllBytes(self):
        packet = a2b('ffffff')
        self.ser.write.return_value = 2
        with pytest.raises(DeviceError) as e:
            self.dev.write_pkg(packet)
        assert e.value.message == "Couldn't write all bytes!"

    def test_read_pkg_OnlyHeader(self):
        pkg = a2b('fd0200bb81002d')
        read_bytes = [pkg[x] for x in range(0, len(pkg))]
        self.ser.inWaiting.return_value = 1
        self.ser.read.side_effect = read_bytes
        expected = [call() for x in read_bytes]

        assert self.dev.read_pkg() == pkg
        assert self.ser.read.call_args_list == expected
        assert self.ser.inWaiting.call_args_list == expected

    def test_read_pkg_OnlyHeaderWithTimeout(self):
        self.ser.inWaiting.return_value = 0
        self.dev.TIMEOUT = 0.1
        with pytest.raises(DeviceError) as e:
            self.dev.read_pkg()
        assert e.value.message == 'Timeout reading header!'

    def test_read_pkg_HeaderAndData(self):
        header = a2b('000a05bb8100aa')
        data = a2b('bb810000cc')
        pkg = header + data
        read_bytes = [pkg[x] for x in range(0, len(pkg))]
        self.ser.read.side_effect = read_bytes
        self.ser.inWaiting.return_value = 1
        expected = [call() for x in read_bytes]

        assert self.dev.read_pkg() == pkg
        assert self.ser.read.call_args_list == expected
        assert self.ser.inWaiting.call_args_list == expected

    def test_read_pkg_HeaderAndDataWithTimeout(self):
        pkg = a2b('000a05bb8100aa')

        in_waiting = [1, 1, 1, 1, 1, 1, 1]

        def side_effect():
            if in_waiting:
                return in_waiting.pop()
            return 0

        self.ser.inWaiting.side_effect = side_effect
        read_bytes = [pkg[x] for x in range(0, len(pkg))]
        self.ser.read.side_effect = read_bytes
        self.dev.TIMEOUT = 0.1
        with pytest.raises(DeviceError) as e:
            self.dev.read_pkg()
        assert e.value.message == 'Timeout reading data!'

    def test_read_bytes(self):
        pkg = a2b('ffff')
        self.ser.inWaiting.side_effect = [1, 1]
        self.ser.read.side_effect = [pkg[0], pkg[1]]
        expected = [call(), call()]

        assert self.dev.read_bytes(2) == pkg
        assert self.ser.inWaiting.call_args_list == expected
        assert self.ser.read.call_args_list == expected

    def test_read_bytes_WithTimeout(self):
        self.ser.inWaiting.return_value = 0
        self.dev.TIMEOUT = 0.1
        with pytest.raises(DeviceError) as e:
            self.dev.read_bytes(1)
        assert e.value.message == 'Timeout reading bytes!'

    def test_read(self):
        pkg = a2b('ff')
        self.ser.inWaiting.return_value = 1
        self.ser.read.return_value = pkg
        assert self.dev.read() == pkg
        self.ser.inWaiting.assert_called_once_with()
        self.ser.read.assert_called_once_with()

    def test_read_something_ButGetNothing(self):
        empty_string = ''
        self.ser.inWaiting.return_value = 0
        assert self.dev.read() == empty_string
