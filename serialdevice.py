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
import binascii
from serial import Serial, SerialException
from serial import EIGHTBITS, PARITY_ODD, STOPBITS_TWO

class SerialDeviceError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SerialDevice(Serial):
    """ Wrapper class for pyserial.
    
    This class takes care of the settings for the Serial Port and provides
    a command called talk() which takes care of sending a packet and recieving
    the answer.
    """
    def __init__(self, port):
        self.serial_for_url = port
        Serial.__init__(self)
        self.baudrate = 57600
        self.bytesize = EIGHTBITS
        self.parity = PARITY_ODD
        self.stopbits = STOPBITS_TWO
        self.xonxoff = 0
        self.rtscts = 0
        self.dsrdtr = 0
        
        if os.name == 'posix':
            self.timeout = 0
        elif os.name == 'nt':
            self.timeout = 1
      
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, self._handler)
        signal.alarm(5)
        self.open()
        self.flush()
        signal.alarm(0) # Disable the alarm
        
    def _handler(signum, frame):
        raise SerialDeviceError("Couldn't open device!")
    
    def _write(self, packet):
        if os.name == 'posix':
            fileno = self.fileno()
            while True:
                readable, writeable, excepts = select([], [fileno], [], 0.1)
                if fileno in writeable:
                    length = self.write(packet)
                    break
        elif os.name == 'nt':
            length = self.write(packet)
        return length
    
    def _read(self):
        if os.name == 'posix':
            fileno = self.fileno()
            while True:
                readable, writeable, excepts = select([], [fileno], [], 0.1)
                if fileno in readable:
                    header = self.read(7)
                    if len(header) != 7:
                        raise SerialDeviceError('recieved header packet has false length')
                    length = int(binascii.b2a_hex(header[3]), 16)
                    data = self.read(length)
                    packet = header + data
                    break
        elif os.name == 'nt':
            header = self.read(7)
            if len(header) != 7:
                raise SerialDeviceError('recieved header packet has false length')
            length = int(binascii.b2a_hex(header[3]), 16)
            data = self.read(length)
            packet = header + data
        return packet
    
    def talk(self, packet):
        self._write(packet)
        responce = self._read()
        return responce
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()