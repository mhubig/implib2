#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (c) 2009-2012, Markus Hubig <mhubig@imko.de>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import sys, re
import signal
from binascii import b2a_hex as b2a
from packet import Packet, PacketException
from serialdevice import SerialDevice, SerialDeviceException

class SnifferException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Sniffer(Packet):
    def __init__(self, port_pc, port_bus):
        self.pc  = SerialDevice(port_pc)
        self.bus = SerialDevice(port_bus)
        
        # handling of CTRL-C
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signal, frame):
        print 'Break: You pressed Ctrl+C!'
        self.pc.close_device()
        self.bus.close_device()
        sys.exit(0)
    
    def open_ports(self):
        self.pc.open_device()
        self.bus.open_device()
       
    def read_pc(self, length=False):
        if not length:
            return self.pc.read()
        else:
            return b2a(self.pc.ser.read(length))
        
    def read_bus(self, legth=False):
        if not length:
            return self.bus.read()
        else:
            return b2a(self.bus.ser.read(length))

    def flush_pc(self):
        self.pc.ser.flush()
        
    def flush_bus(self):
        self.bus.ser.flush()

    def listen(self):
        while True:
            packet_pc = self.read_pc()
            packet_pc = self.unpack(packet_pc)
            
            if packet['cmd'] == 0x04:
                name = "Get Short Ack"
                packet_bus = self.read_bus(1)
                self.flush_bus()
            
            elif packet['cmd'] == 0x06:
                name = "Get Ack for Range"
                packet_bus = self.read_bus(1)
                self.flush_bus()
                
            else:
                name = "Plain Command"
                packet_bus = self.read_bus()
                packet_bus = self.unpack(packet_bus)
                
            print "--------------------------------------------"
            print "Name:      ", name
            print "Packet PC: ", packet_pc
            print "Packet BUS:", packet_bus
                 
if __name__ == "__main__":
    sniffer = Sniffer('/dev/tty.usbserial-FTESNJKP', '/dev/tty.usbserial-FTESNKRF')
    sniffer.open_ports()
    sniffer.listen()
