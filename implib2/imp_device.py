# -*- coding: UTF-8 -*-

import time
import struct

import serial


class DeviceError(Exception):
    pass


class Device:

    def __init__(self, port):
        self.ser = serial.serial_for_url(port, do_not_open=True)
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_ODD
        self.ser.stopbits = serial.STOPBITS_TWO
        self.ser.timeout = 0.1  # 100ms
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.dsrdtr = 0
        self.is_open = False

    def open_device(self, baudrate=9600):
        self.ser.baudrate = baudrate
        self.ser.open()
        self.ser.flush()
        time.sleep(0.05)  # 50ms
        self.is_open = True

    def close_device(self):
        try:
            self.ser.flush()
            self.ser.close()
        except serial.SerialException:
            pass
        finally:
            time.sleep(0.05)  # 50ms
            self.is_open = False

    def write_pkg(self, packet):
        if not self.is_open:
            raise DeviceError("Couldn't write packet, device is closed!")

        bytes_send = self.ser.write(packet)

        if not bytes_send == len(packet):
            raise DeviceError("Couldn't write all bytes!")

        return True

    def read_pkg(self):
        if not self.is_open:
            raise DeviceError("Couldn't read packet, device is closed!")

        # read header, always 7 bytes
        header = self.ser.read(7)

        if len(header) < 7:
            raise DeviceError('Timeout reading header!')

        if isinstance(header, str):
            length = struct.unpack('<B', header[2])[0]  # py27
        else:
            length = header[2]                          # py33

        if length == 0:
            return header

        data = self.ser.read(length)

        if len(data) < length:
            raise DeviceError('Timeout reading data!')

        return header + data

    def read_bytes(self, length):
        if not self.is_open:
            raise DeviceError("Couldn't read bytes, device is closed!")

        data = self.ser.read(length)

        if len(data) < length:
            raise DeviceError('Timeout reading bytes!')

        return data

    def read(self):
        if not self.is_open:
            raise DeviceError("Couldn't read byte, device is closed!")

        byte = self.ser.read(1)
        self.ser.flushInput()

        return byte
