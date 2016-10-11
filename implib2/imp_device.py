#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
