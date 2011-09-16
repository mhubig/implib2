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
from binascii import b2a_hex as b2a
from binascii import a2b_hex as a2b
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet import reactor

class Noisy(Protocol):
    def __init__(self, delay, data):
        self.delay = delay
        self.data = data

    def stop(self):
        self.transport.unregisterProducer()
        self.transport.loseConnection()
        reactor.stop()

    def resumeProducing(self):
        self.transport.write(self.data)

    def connectionMade(self):
        self.transport.registerProducer(self, False)
        reactor.callLater(self.delay, self.stop)

factory = ClientFactory()
factory.protocol = lambda: Noisy(60, "hello server")
reactor.connectTCP(host, port, factory)
reactor.run()


class SerialdeviceException(Exception):
    pass

class Serialdevice(object):
    """ Class for sending and recieving IMPBUS2 Packets via a serial line.
    
    This class takes care of the settings for the Serial Port and provides
    the commands write, read and one called talk() which takes care of sending
    a packet and recieving the answer.
    """
    def __init__(self, port, baudrate=9600):
        self.DEBUG = False
        
        try:
            self.ser = serial_for_url(port)
        except SerialException as e:
            raise IMPSerialDeviceException(e.message)
        
        self.ser.baudrate = baudrate
        self.ser.bytesize = EIGHTBITS
        self.ser.parity = PARITY_ODD
        self.ser.stopbits = STOPBITS_TWO
        self.ser.timeout = None # Wait forever
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.dsrdtr = 0
    
        # open the device
        self.open_device()
    
    def _open_device_handler(self, signum, frame):
        raise IMPSerialDeviceException("Couldn't open device!")
        
    def _close_device_handler(self, signum, frame):
        raise IMPSerialDeviceException("Couldn't close device!")
    
    def _write_device_handler(self, signum, frame):
        raise IMPSerialDeviceException("Writing to device timed out!")
        
    def _read_device_handler(self, signum, frame):
        raise IMPSerialDeviceException("Reading from device timed out!")
    
    def open_device(self):
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._open_device_handler)
        signal.alarm(2)
        self.ser.open()
        if self.DEBUG: print 'Device opened:', self.ser.name
        self.ser.flush()
        signal.alarm(0) # Disable the alarm
        
    def close_device(self):
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._close_device_handler)
        signal.alarm(2)
        self.ser.flush()
        self.ser.close()
        if self.DEBUG: print 'Device closed:', self.ser.name
        signal.alarm(0) # Disable the alarm
    
    def write_package(self, packet):
        """ Writes IMPBUS2 packet to the serial line.
        
        Packet must be a pre-build HEX string. Returns the
        length in Bytes of the string written. 
        """
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._write_device_handler)
        signal.alarm(2)
        bytes_send = self.ser.write(a2b(packet))
        signal.alarm(0) # Disable the alarm
        #time.sleep(0.018)
        time.sleep(0.1)
        if self.DEBUG: print 'Packet send:', packet, 'Length:', bytes_send
        return bytes_send
        
    def read_package(self):
        """ Read IMPBUS2 packet from serial line.

        It automatically calculates the length from the header
        information and Returns the recieved packet as HEX string.
        """
        self.ser.timeout = 0 # Wait forever
        
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._read_device_handler)
        signal.alarm(2)
        
        header = ''
        # read header, always 7 bytes
        while len(header) < 7:
            byte = self.ser.read()
            if len(byte) == 1:
                header += byte
        if self.DEBUG: print 'Header read:', b2a(header)
        length = int(b2a(header)[4:6], 16)
        
        # read data, length is known from header
        data = self.ser.read(length)
        packet = b2a(header + data)
        signal.alarm(0) # Disable the alarm
        if self.DEBUG: print 'Packet read:', packet, 'Length:', len(packet)/2
        return packet
        
    def read_bytes(self, length):
        """ Tries to read <length>-bytes from the serial line.
        
        Methode to read a given amount of byter from the serial
        line. Returns the result as HEX string.
        """
        self.ser.timeout = None # Wait forever
        
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._read_device_handler)
        signal.alarm(2)
        bytes = b2a(self.ser.read(length))
        signal.alarm(0) # Disable the alarm
        if self.DEBUG: print 'Bytes Read:', bytes
        return bytes
        
    def read_something(self):
        """ Tries to read _one_ byte from the serial line.

        This methode shold be as fast as possible. Returns
        True or False. Useable for scanning the bus. 
        """
        self.ser.timeout = 0
        # Set the signal handler and a 2-seconds alarm
        signal.signal(signal.SIGALRM, self._read_device_handler)
        signal.alarm(2)
        stuff = self.ser.read()
        signal.alarm(0) # Disable the alarm
        if not stuff:
            if self.DEBUG: print 'Byte Read: False'
            return False
        if self.DEBUG: print 'Byte Read: True'
        return True
    
    def talk(self, packet):
        """ Writes an IMPBUS2 Package and reads the responce packet """
        self.write_packet(packet)
        responce = self.read_packet()
        return responce
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()