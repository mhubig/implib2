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
from serial import Serial, SerialException
from serial import EIGHTBITS, PARITY_ODD, STOPBITS_TWO
import binascii

class SerialDevice(Serial):

    def __init__(self, port):
        Serial.__init__(self)
        self.port = port
        self.baudrate = 57600
        self.bytesize = EIGHTBITS
        self.parity = PARITY_ODD
        self.stopbits = STOPBITS_TWO
        self.timeout = 0
        self.xonxoff = 0
        self.rtscts = 0
        self.dsrdtr = 0
        self.open()
        self.flush()
    
    def _write(self, packet):
        fileno = self.fileno()
        while True:
            readable, writeable, excepts = select([], [fileno], [], 0.1)
            if fileno in writeable:
                length = self.write(packet)
                break
        return length
    
    def _read(self):
        fileno = self.fileno()
        while True:
            readable, writeable, excepts = select([], [fileno], [], 0.1)
            if fileno in readable:
                header = self.read(7)
                length = int(binascii.b2a_hex(header[3]), 16)
                data = self.read(length)
                packet = header + data
                break
        return packet
    
    def talk(self, packet):
        self._write(packet)
        responce = self._read()
        return responce
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()