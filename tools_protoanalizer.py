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

import sys, re
import signal
from binascii import b2a_hex as b2a
from packet import Packet, PacketException
from serialdevice import SerialDevice, SerialDeviceException

class SnifferException(Exception):
    pass

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
