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
from binascii import b2a_hex as b2a
from binascii import a2b_hex as a2b
from serial import Serial, SerialException
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
        self.DEBUG = True
        self.TIMEOUT = 2
        self.BAUDRATE = baudrate
        self.PORT = port
        
        try:
            self.ser = Serial()
        except SerialException as e:
            raise SerialDeviceException(e.message)
        
    def open_device(self):
        self.ser.port     = self.PORT
        self.ser.baudrate = self.BAUDRATE
        self.ser.bytesize = EIGHTBITS
        self.ser.parity   = PARITY_ODD
        self.ser.stopbits = STOPBITS_TWO
        self.ser.timeout  = 0 # act nonblocking
        self.ser.xonxoff  = 0
        self.ser.rtscts   = 0
        self.ser.dsrdtr   = 0
        self.ser.open()
        self.ser.flush()
        if self.DEBUG: print 'Device opened:', self.ser.name
        
    def close_device(self):
        self.ser.flush()
        self.ser.close()
        if self.DEBUG: print 'Device closed:', self.ser.name
    
    def write_package(self, packet):
        """ Writes IMPBUS2 packet to the serial line.
        
        Packet must be a pre-build HEX string. Returns the
        length in Bytes of the string written. 
        """
        bytes_send = self.ser.write(a2b(packet))
        time.sleep(0.1)
        if self.DEBUG: print 'Packet send:', packet, 'Length:', bytes_send
        return bytes_send
        
    def read_package(self):
        """ Read IMPBUS2 packet from serial line.

        It automatically calculates the length from the header
        information and Returns the recieved packet as HEX string.
        """
        
        # read header, always 7 bytes
        header = str()
        length = 7
        tic = time.time()
        while (time.time() - tic < self.TIMEOUT) and (len(header) < length): 
            if self.ser.inWaiting(): header += self.ser.read()
        if self.DEBUG: print 'Header read:', b2a(header), 'Length:', len(header)
        
        if len(header) < length:
            raise SerialDeviceException('TimeoutError reading header!')
        
        # read data, length is known from header
        data = str()
        length = int(b2a(header)[4:6], 16)
        print "---> Length:", length
        tic = time.time()
        while (time.time() - tic < self.TIMEOUT) and (len(data) < length):
            if self.ser.inWaiting(): data += self.ser.read()
        print "Timeout:", time.time() - tic > self.TIMEOUT
        if self.DEBUG: print 'Data read:', b2a(data), 'Length:', len(data)
        
        if len(data) < length:
            raise SerialDeviceException('TimeoutError reading data!')
            
        packet = b2a(header + data)
        if self.DEBUG: print 'Packet read:', packet, 'Length:', len(packet)/2
        return packet
        
    def read_bytes(self, length):
        """ Tries to read <length>-bytes from the serial line.
        
        Methode to read a given amount of byter from the serial
        line. Returns the result as HEX string.
        """
        bytes = str()
        tic = time.time()
        while (time.time() - tic < self.TIMEOUT) and (len(bytes) < length): 
            if self.ser.inWaiting(): bytes += self.ser.read()
        if self.DEBUG: print 'Bytes read:', b2a(bytes)
        
        if len(bytes) < length:
            raise SerialDeviceException('TimeoutError reading header!')
        
        return b2a(bytes)
        
    def read_something(self):
        """ Tries to read _one_ byte from the serial line.

        This methode shold be as fast as possible. Returns
        True or False. Useable for scanning the bus. 
        """
        state = (len(self.ser.read()) == 1)
        if self.DEBUG: print 'Byte Read:', state
        return state
    
    def talk(self, packet):
        """ Writes an IMPBUS2 Package and reads the responce packet """
        self.write_packet(packet)
        return self.read_packet()
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()