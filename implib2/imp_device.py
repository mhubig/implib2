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

import time
import struct

import serial


class DeviceError(Exception):
    pass


class Device(object):

    def __init__(self, port):
        self.ser = serial.serial_for_url(port, do_not_open=True)
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_ODD
        self.ser.stopbits = serial.STOPBITS_TWO
        self.ser.timeout = 0.1  # 100ms
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.dsrdtr = 0

    def open_device(self, baudrate=9600):
        self.ser.baudrate = baudrate
        self.ser.open()
        self.ser.flush()
        time.sleep(0.05)  # 50ms

    def close_device(self):
        try:
            self.ser.flush()
            self.ser.close()
        except serial.SerialException:
            pass
        finally:
            time.sleep(0.05)  # 50ms

    def write_pkg(self, packet):
        bytes_send = self.ser.write(packet)
        if not bytes_send == len(packet):
            raise DeviceError("Couldn't write all bytes!")
        return True

    def read_pkg(self):
        # read header, always 7 bytes
        header = self.ser.read(7)

        if len(header) < 7:
            raise DeviceError('Timeout reading header!')

        length = struct.unpack('<B', header[2])[0]

        if length == 0:
            return header

        data = self.ser.read(length)

        if len(data) < length:
            raise DeviceError('Timeout reading data!')

        return header + data

    def read_bytes(self, length):
        data = self.ser.read(length)

        if len(data) < length:
            raise DeviceError('Timeout reading bytes!')

        return data

    def read(self):
        byte = self.ser.read(1)
        self.ser.flushInput()
        return byte
