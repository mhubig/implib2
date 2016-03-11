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

from binascii import a2b_hex as a2b

import pytest
import serial  # noqa pylint: disable=unused-import
from mock import patch, call

from implib2.imp_device import Device, DeviceError


# pylint: disable=invalid-name, attribute-defined-outside-init
class TestPackage(object):

    def setup(self):
        with patch('serial.Serial') as mock:
            self.ser = mock()
            self.dev = Device('/dev/ttyS0')

    def test_open_device(self):
        self.dev.open_device()
        self.ser.open.assert_called_once_with()
        self.ser.flush.assert_called_once_with()

    def test_close_device(self):
        self.dev.close_device()
        self.ser.flush.assert_called_once_with()
        self.ser.close.assert_called_once_with()

    def test_close_device_FlushThowsException(self):
        self.ser.flush.side_effect = serial.SerialException()
        self.dev.close_device()
        self.ser.flush.assert_called_once_with()
        self.ser.close.assert_not_called()

    def test_close_device_CloseThowsException(self):
        self.ser.close.side_effect = serial.SerialException()
        self.dev.close_device()
        self.ser.flush.assert_called_once_with()
        self.ser.close.assert_called_once_with()

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
        header = a2b('fd0200bb81002d')
        self.ser.read.side_effect = [header]

        assert self.dev.read_pkg() == header
        assert self.ser.read.call_args_list == [call(7)]

    def test_read_pkg_OnlyHeaderWithTimeout(self):
        with pytest.raises(DeviceError) as e:
            self.dev.read_pkg()
        assert e.value.message == 'Timeout reading header!'

    def test_read_pkg_HeaderAndData(self):
        header = a2b('000a05bb8100aa')
        data = a2b('bb810000cc')
        self.ser.read.side_effect = [header, data]

        assert self.dev.read_pkg() == header + data
        assert self.ser.read.call_args_list == [call(7), call(5)]

    def test_read_pkg_HeaderAndDataWithTimeout(self):
        pkg = a2b('000a05bb8100aa')
        self.ser.read.side_effect = [pkg, b'']
        with pytest.raises(DeviceError) as e:
            self.dev.read_pkg()

        assert e.value.message == 'Timeout reading data!'
        assert self.ser.read.call_args_list == [call(7), call(5)]

    def test_read_bytes(self):
        pkg = a2b('ffff')
        self.ser.read.side_effect = [pkg]

        assert self.dev.read_bytes(2) == pkg
        self.ser.read.assert_called_once_with(2)

    def test_read_bytes_WithTimeout(self):
        with pytest.raises(DeviceError) as e:
            self.dev.read_bytes(1)
        assert e.value.message == 'Timeout reading bytes!'

    def test_read(self):
        pkg = a2b('ff')
        self.ser.read.return_value = pkg
        assert self.dev.read() == pkg
        self.ser.read.assert_called_once_with(1)
        self.ser.flushInput.assert_called_once_with()

    def test_read_something_ButGetNothing(self):
        empty_string = ''
        self.ser.read.return_value = empty_string
        assert self.dev.read() == empty_string
        self.ser.read.assert_called_once_with(1)
        self.ser.flushInput.assert_called_once_with()
