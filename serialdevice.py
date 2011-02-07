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
import time
import signal
#from singleton import Singleton
from binascii import b2a_hex as b2a
from binascii import a2b_hex as a2b
from select import select
from serial import serial_for_url, Serial, SerialException
from serial import EIGHTBITS, PARITY_ODD, STOPBITS_TWO

class SerialDeviceException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SerialDevice(object):
    """ Class for sending and recieving IMPBUS2 Packets via a serial line.
    
    This class takes care of the settings for the Serial Port and provides
    the commands write, read and one called talk() which takes care of sending
    a packet and recieving the answer.
    """
    def __init__(self, port, baudrate=9600):
        self.DEBUG = False
        self.ser = serial_for_url(port)
        self.ser.nonblocking()
        self.ser.baudrate = baudrate
        self.ser.bytesize = EIGHTBITS
        self.ser.parity = PARITY_ODD
        self.ser.stopbits = STOPBITS_TWO
        self.ser.timeout = 0
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
        raise SerialDeviceException("Reading from device timed out!")
    
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
    
    def write_package(self, packet):
        """ Writes IMPBUS2 packet to the serial line.
        
        Packet must be a pre-build HEX string. Returns the
        length in Bytes of the string written. 
        """
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._write_device_handler)
        signal.alarm(2)
        length = self.ser.write(a2b(packet))
        signal.alarm(0) # Disable the alarm
        time.sleep(0.018)
        return length
        
    def read_package(self):
        """ Read IMPBUS2 packet from serial line.

        It automatically calculates the length from the header
        information and Returns the recieved packet as HEX string.
        """
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._read_device_handler)
        signal.alarm(2)
        
        # read header, always 7 bytes
        header = ''
        while len(header) < 7:
            header += self.ser.read()
        length = int(b2a(header)[4:6], 16)
        
        # read data, length is known from header
        data = ''
        while len(data) < length:
            data += self.ser.read()
        
        packet = header + data
        signal.alarm(0) # Disable the alarm
        return b2a(packet)
        
    def read_bytes(self, length):
        """ Tries to read <length>-bytes from the serial line.
        
        Methode to read a given amount of byter from the serial
        line. Returns the result as HEX string.
        """
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._read_device_handler)
        signal.alarm(2)
        # getting the fileno for select()
        fileno = self.ser.fileno()            
        bytes = ''
        while len(bytes) < length:
                bytes += self.ser.read()
        signal.alarm(0) # Disable the alarm
        return b2a(bytes)
        
    def read_something(self):
        """ Tries to read _one_ byte from the serial line.

        This methode shold be as fast as possible. Returns
        True or False. Useable for scanning the bus. 
        """
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._read_device_handler)
        signal.alarm(2)
        stuff = self.ser.read()
        signal.alarm(0) # Disable the alarm
        if not stuff: return False
        return True
    
    def talk(self, packet):
        """Writes an IMPBUS2 Package and reads the responce packet"""
        self.write_packet(packet)
        responce = self.read_packet()
        return responce
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()