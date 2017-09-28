# -*- coding: UTF-8 -*-

import pytest
import serial  # noqa

try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call

from binascii import a2b_hex as a2b

from implib2.imp_device import Device, DeviceError


class TestPackage:

    def setup(self):
        with patch('serial.Serial') as mock:
            self.ser = mock()
            self.dev = Device('/dev/ttyS0')

    def test_open_device(self):
        self.dev.open_device()
        self.ser.open.assert_called_once_with()
        self.ser.flush.assert_called_once_with()
        assert self.dev.is_open is True

    def test_close_device(self):
        self.dev.close_device()
        self.ser.flush.assert_called_once_with()
        self.ser.close.assert_called_once_with()
        assert self.dev.is_open is False

    def test_close_device_FlushThowsException(self):
        self.ser.flush.side_effect = serial.SerialException()
        self.dev.close_device()
        self.ser.flush.assert_called_once_with()
        self.ser.close.assert_not_called()
        assert self.dev.is_open is False

    def test_close_device_CloseThowsException(self):
        self.ser.close.side_effect = serial.SerialException()
        self.dev.close_device()
        self.ser.flush.assert_called_once_with()
        self.ser.close.assert_called_once_with()
        assert self.dev.is_open is False

    def test_write_pkg(self):
        packet = a2b('ffffff')
        self.ser.write.return_value = 3
        self.dev.is_open = True
        assert self.dev.write_pkg(packet)
        self.ser.write.assert_called_once_with(packet)

    def test_write_pkg_FailsIfDeviceIsNotOpen(self):
        packet = a2b('ffffff')
        self.dev.is_open = False
        with pytest.raises(DeviceError, message="Couldn't write packet, device is closed!"):
            self.dev.write_pkg(packet)
        self.ser.write.assert_not_called()

    def test_write_pkg_ButNotAllBytes(self):
        packet = a2b('ffffff')
        self.ser.write.return_value = 2
        with pytest.raises(DeviceError, message="Couldn't write all bytes!"):
            self.dev.is_open = True
            self.dev.write_pkg(packet)

    def test_read_pkg_FailsIfDeviceIsNotOpen(self):
        with pytest.raises(DeviceError, message="Couldn't read packet, device is closed!"):
            self.dev.is_open = False
            self.dev.read_pkg()
        self.ser.read.assert_not_called()

    def test_read_pkg_OnlyHeader(self):
        header = a2b('fd0200bb81002d')
        self.ser.read.side_effect = [header]
        self.dev.is_open = True

        assert self.dev.read_pkg() == header
        assert self.ser.read.call_args_list == [call(7)]

    def test_read_pkg_OnlyHeaderWithTimeout(self):
        with pytest.raises(DeviceError, message='Timeout reading header!'):
            self.dev.is_open = True
            self.dev.read_pkg()

    def test_read_pkg_HeaderAndData(self):
        header = a2b('000a05bb8100aa')
        data = a2b('bb810000cc')
        self.ser.read.side_effect = [header, data]
        self.dev.is_open = True

        assert self.dev.read_pkg() == header + data
        assert self.ser.read.call_args_list == [call(7), call(5)]

    def test_read_pkg_HeaderAndDataWithTimeout(self):
        pkg = a2b('000a05bb8100aa')
        self.ser.read.side_effect = [pkg, b'']
        with pytest.raises(DeviceError, message='Timeout reading data!'):
            self.dev.is_open = True
            self.dev.read_pkg()

        assert self.ser.read.call_args_list == [call(7), call(5)]

    def test_read_bytes_FailsIfDeviceIsNotOpen(self):
        with pytest.raises(DeviceError, message="Couldn't read bytes, device is closed!"):
            self.dev.is_open = False
            self.dev.read_bytes(2)
        self.ser.read.assert_not_called()

    def test_read_bytes(self):
        pkg = a2b('ffff')
        self.ser.read.side_effect = [pkg]
        self.dev.is_open = True

        assert self.dev.read_bytes(2) == pkg
        self.ser.read.assert_called_once_with(2)

    def test_read_bytes_WithTimeout(self):
        with pytest.raises(DeviceError, message='Timeout reading bytes!'):
            self.dev.is_open = True
            self.dev.read_bytes(1)

    def test_read_FailsIfDeviceIsNotOpen(self):
        with pytest.raises(DeviceError, message="Couldn't read byte, device is closed!"):
            self.dev.is_open = False
            self.dev.read()
        self.ser.read.assert_not_called()

    def test_read(self):
        pkg = a2b('ff')
        self.ser.read.return_value = pkg
        self.dev.is_open = True
        assert self.dev.read() == pkg
        self.ser.read.assert_called_once_with(1)
        self.ser.flushInput.assert_called_once_with()

    def test_read_something_ButGetNothing(self):
        empty_string = ''
        self.ser.read.return_value = empty_string
        self.dev.is_open = True
        assert self.dev.read() == empty_string
        self.ser.read.assert_called_once_with(1)
        self.ser.flushInput.assert_called_once_with()
