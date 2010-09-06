#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datablock import Datablock, DatablockError
from packet import Packet,PacketError
import binascii

class CommandsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Commands(Packet,Datablock):
    """ This Class provides funktions to comunicate with a IMPBUS probe.
    
    >>> from commands import Commands, CommandsError
    >>> c = Commands()
    >>> c.get_negative_acknowledge()
    0
    """
    
    def __init__(self):
        Packet.__init__(self)
        Datablock.__init__(self)
        
    def get_negative_acknowledge(self,comm=None):
        """ Command to identify a single module.
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        """
        package = self.pack(serno=16777215,cmd=0x08)
        if not comm:
            serial = 0
        else:
            response = comm.talk(package)
            packet = self.unpack(response)
            serial = packet[data][0:6]
        return serial
        
    def set_serial_number(self,serial,comm=None):
        """ Command to set the serial number of the module.
        
        
        """
        no_param = 0x01
        ad_param = 0x00
        param = serial
        data = self.assemble(no_param,ad_param,param)
        package = self.pack(serno=0,cmd=0x11,data=data)
    
    

    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
