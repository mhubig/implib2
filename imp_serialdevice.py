#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011, Markus Hubig <mhubig@imko.de>

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
from struct import pack, unpack
from binascii import b2a_hex as b2a, a2b_hex as a2b

#from tools_debug import trace

class SerialDeviceError(Exception):
    pass

class SerialDevice(object):
    """ Class for sending and recieving IMPBUS2 Packets via a serial line.
    
    This class takes care of the settings for the Serial Port and provides
    the commands write, read and one called talk() which takes care of sending
    a packet and recieving the answer.
    """
    def __init__(self, port):
        self.PORT = port
        self.TIMEOUT = 5
        
        try:
            self.ser = serial.serial_for_url(url=port, do_not_open=True)
        except AttributeError:
            self.ser = serial.Serial(port=None)
        
    def open_device(self, baudrate=9600):
        self.ser.port     = self.PORT
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity   = serial.PARITY_ODD
        self.ser.stopbits = serial.STOPBITS_TWO
        self.ser.timeout  = 0 # act nonblocking
        self.ser.xonxoff  = 0
        self.ser.rtscts   = 0
        self.ser.dsrdtr   = 0
        self.ser.open()
        self.ser.flush()
        
    def close_device(self):
        try:
            self.ser.flush()
            self.ser.close()
        except:
            pass
        
    def write_pkg(self, packet):
        """ Writes IMPBUS2 packet to the serial line.
        
        Packet must be a pre-build BYTE string. Returns the
        length in Bytes of the string written. 
        """
        bytes_send = self.ser.write(packet)
        if not bytes_send == len(packet):
            raise SerialDeviceError("Couldn't write all bytes!")
        
        return True
        
    def read_pkg(self):
        """ Read IMPBUS2 packet from serial line.
        
        It automatically calculates the length from the header
        information and Returns the recieved packet as BYTE string.
        """
        # read header, always 7 bytes
        header = str()
        length = 7
        tic = time.time()
        while (time.time() - tic < self.TIMEOUT) and (len(header) < length): 
            if self.ser.inWaiting(): header += self.ser.read()
        
        if len(header) < length:
            raise SerialDeviceError('Timeout reading header!')
        
        # read data, length is known from header
        data = str()
        length = unpack('<B',header[2])[0]
        tic = time.time()
        while (time.time() - tic < self.TIMEOUT) and (len(data) < length):
            if self.ser.inWaiting(): data += self.ser.read()
        
        if len(data) < length:
            raise SerialDeviceError('Timeout reading data!')
        
        return header + data
        
    def read_bytes(self, length):
        """ Tries to read <length>-bytes from the serial line.
        
        Methode to read a given amount of byter from the serial
        line. Returns the result as BYTE string.
        """
        bytes = str()
        tic = time.time()
        while (time.time() - tic < self.TIMEOUT) and (len(bytes) < length): 
            if self.ser.inWaiting(): bytes += self.ser.read()
        
        if len(bytes) < length:
            raise SerialDeviceError('Timeout reading bytes!')
        
        return bytes
        
    def read_something(self):
        """ Tries to read _one_ byte from the serial line.
        
        This methode shold be as fast as possible. Returns
        True or False. Useable for scanning the bus. 
        """
        bytes = str()
        tic = time.time()
        while (time.time() - tic < 0.25) and (len(bytes) < 1): 
            if self.ser.inWaiting(): bytes += self.ser.read()
        
        return bytes
        
    def talk(self, packet):
        """ Writes an IMPBUS2 Package and reads the responce packet """
        self.write_pkg(packet)
        return self.read_pkg()
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()

