#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2012, Markus Hubig <mhubig@imko.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import os
import signal
from singleton import Singleton
from binascii import b2a_hex as b2a
from binascii import a2b_hex as a2b
from serial import serial_for_url, Serial, SerialException
from serial import EIGHTBITS, PARITY_ODD, STOPBITS_TWO

class SerialDeviceException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SerialDevice(Singleton):
    """ Class for sending and recieving IMPBUS2 Packets via a serial line.
    
    This class takes care of the settings for the Serial Port and provides
    the commands write, read and one called talk() which takes care of sending
    a packet and recieving the answer.
    """
    def __init__(self, port, baudrate=57600):
        self.DEBUG = False
        self.ser = serial_for_url(port)
        self.ser.baudrate = baudrate
        self.ser.bytesize = EIGHTBITS
        self.ser.parity = PARITY_ODD
        self.ser.stopbits = STOPBITS_TWO
        self.ser.timeout = None
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.dsrdtr = 0
    
    def _open_device_handler(self, signum, frame):
        raise SerialDeviceException("Couldn't open device!")
        
    def _close_device_handler(self, signum, frame):
        raise SerialDeviceException("Couldn't close device!")
    
    def _write_device_handler(self, signum, frame):
        raise SerialDeviceException("Writing to device timed out!")
        
    def _read_device_handler(self, signum, frame):
        raise SerialDeviceException("Reading to device timed out!")
    
    def open_device(self):
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._open_device_handler)
        signal.alarm(2)
        self.ser.open()
        self.ser.flush()
        signal.alarm(0) # Disable the alarm
        
    def close_device(self):
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._close_device_handler)
        signal.alarm(2)
        self.ser.flush()
        self.ser.close()
        signal.alarm(0) # Disable the alarm
    
    def write(self, packet):
        """
        Writes a IMPBUS2 packet to the serial line. Packet is a prebuild
        HEX string. Returns the length in Bytes of the string written. 
        """
        fileno = self.ser.fileno()
        while True:
            readable, writeable, excepts = select([], [fileno], [], 0.1)
            if fileno in writeable:
                # Set the signal handler and a 2-seconds alarm
                signal.signal(signal.SIGALRM, self._write_device_handler)
                signal.alarm(2)
                length = self.ser.write(a2b(packet))
                signal.alarm(0) # Disable the alarm
                break
        return length
    
    def read(self):
        """
        Reads a IMPBUS2 packet from the serial Line. It automatically
        calculates the length from the header information. Returns the
        recieved packet as a HEX string.
        """
        fileno = self.fileno()
        while True:
            readable, writeable, excepts = select([], [fileno], [], 0.1)
            if fileno in readable:
                # Set the signal handler and a 2-seconds alarm
                signal.signal(signal.SIGALRM, self._read_device_handler)
                signal.alarm(2)
                header = self.ser.read(7)
                length = int(b2a(header[3]), 16)
                data = self.ser.read(length)
                packet = header + data
                signal.alarm(0) # Disable the alarm
                break
        return packet
    
    def talk(self, packet):
        """Writes an IMPBUS2 Package and reads the responce"""
        self.write(packet)
        responce = self.read()
        return responce
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()