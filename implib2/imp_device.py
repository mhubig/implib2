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
import serial
from struct import unpack


class DeviceError(Exception):
    pass


class Device(object):
    def __init__(self, port):
        self.ser = serial.serial_for_url(port, do_not_open=True)
        self.open_device()

    def _timeout(self, length):
        # pylint: disable=C0321
        if not length:
            return 0
        baudrate = self.ser.baudrate
        return 600.0 / baudrate * length

    def open_device(self, baudrate=9600):
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_ODD
        self.ser.stopbits = serial.STOPBITS_TWO
        self.ser.timeout = 0  # act nonblocking
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.dsrdtr = 0
        self.ser.open()
        self.ser.flush()
        time.sleep(0.050)

    def close_device(self):
        if self.ser.isOpen():
            self.ser.flush()
            self.ser.close()
        time.sleep(0.050)

    def write_pkg(self, packet):
        bytes_send = self.ser.write(packet)
        if not bytes_send == len(packet):
            raise DeviceError("Couldn't write all bytes!")

        return True

    def read_pkg(self):
        # read header, always 7 bytes
        header = str()
        length = 7
        timeout = self._timeout(length)
        tic = time.time()
        while (time.time() - tic < timeout) and (len(header) < length):
            if self.ser.inWaiting():
                header += self.ser.read()

        if len(header) < length:
            raise DeviceError('Timeout reading header!')

        # read data, length is known from header
        data = str()
        length = unpack('<B', header[2])[0]
        timeout = self._timeout(length)
        tic = time.time()
        while (time.time() - tic < timeout) and (len(data) < length):
            if self.ser.inWaiting():
                data += self.ser.read()

        if len(data) < length:
            raise DeviceError('Timeout reading data!')

        return header + data

    def read_bytes(self, length):
        rbs = str()
        timeout = self._timeout(length)
        tic = time.time()
        while (time.time() - tic < timeout) and (len(rbs) < length):
            if self.ser.inWaiting():
                rbs += self.ser.read()

        if len(rbs) < length:
            raise DeviceError('Timeout reading bytes!')

        return rbs

    def read(self):
        byte = bytes()
        if self.ser.inWaiting():
            byte = self.ser.read()

        self.ser.flushInput()
        return byte
