#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# TODO: Implement general purpose set and get commands

from packet import Packet,PacketError

class CommandsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Commands(Packet):
    """ This Class provides funktions to comunicate with a IMPBUS probe.
    
    >>> from commands import Commands, CommandsError
    >>> c = Commands()
    >>> serno = 31001
    >>> event = 0x02
    >>> c.get_negative_acknowledge()
    {'state': '0xfd', 'cmd': '0x8', 'length': 0, 'serno': 16777215}
    None
    0
    >>> c.get_long_acknowledge(serno)
    {'state': '0xfd', 'cmd': '0x2', 'length': 0, 'serno': 31001}
    None
    0
    >>> c.set_SPT_SerialNum(0,serno)
    {'state': '0xfd', 'cmd': '0x11', 'length': 5, 'serno': 0}
    01007919
    0
    >>> c.get_APT_Event(serno)
    {'state': '0xfd', 'cmd': '0x20', 'length': 3, 'serno': 31001}
    0300
    130
    >>> c.set_APT_Event(serno,event)
    {'state': '0xfd', 'cmd': '0x20', 'length': 3, 'serno': 31001}
    0300
    {'state': '0xfd', 'cmd': '0x21', 'length': 4, 'serno': 31001}
    030002
    True
    """
    
    def __init__(self):
        Packet.__init__(self)
               
    def get_negative_acknowledge(self,comm=None):
        """ Command to identify a single module.
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        """
        packet = self.pack(serno=16777215,cmd=0x08)
        if not comm:
            packet = self.unpack(packet)
            print(packet['header'])
            print(packet['data'])
            serno = 0
        else:
            response = comm.talk(packet)
            packet = self.unpack(response)
            data = packet['data']
            serno = data[4:6] + data[2:4] + data[0:2]
        return serno
        
    def get_long_acknowledge(self,serno,comm=None):
        """ Command to PING a specific module.
        
        This command with the number 2 will call up the slave which is
        addressed by its serial number. In return, the slave replies with
        a complete address block. It can be used to test the presence of
        a module in conjunction with the quality of the bus connection.
        """
        packet = self.pack(serno=serno,cmd=0x02)
        if not comm:
            packet = self.unpack(packet)
            print(packet['header'])
            print(packet['data'])
            serno = 0
        else:
            response = comm.talk(packet)
            packet = self.unpack(response)
            header = packet['header']
            serno = header['serno']
        return serno
        
    def set_SPT_SerialNum(self,old_serno,new_serno,comm=None):
        """ Command to set the serial number of the module.
        
        This command writes the new serial into the System Parameter Table.
        No. 0x00, Type 0x04, Location 0x02, Status OR, Name SerialNum, Byte
        Length 4. Fresh modules have always serial number 0.
        """
        packet = self.pack(old_serno,0x11,0x01,new_serno)
        if not comm:
            packet = self.unpack(packet)
            print(packet['header'])
            print(packet['data'])
            state = 0x00
        else:
            response = comm.talk(packet)
            packet = self.unpack(response)
            state = packet['header']['state']
        return state
    
    def get_APT_Event(self,serno,comm=None):
        """ Command to read the Event state from the APT.
        
        The parameter Event is used to control the slave to fulfil the
        different events. They are:
        
        Normal Measure              VNo: 0x00,  DNo: 0x80
        TDR Scan                    VNo: 0x01,  DNo: 0x81
        Analog Out                  VNo: 0x02,  DNo: 0x82
        ASIC                        VNo: 0x03,  DNo: 0x83
        Temperature Compensation    VNo: 0x04,  DNo: 0x84
        Self Test                   VNo: 0x05,  DNo: 0x85
        MatTempSensor               VNo: 0x06,  DNo: 0x86
        
        When the master sets the slave to above mentioned events, the respective
        value number (VNo) should be sent. If the slave has changed the event
        from the present one to desired one, the respective values will be set
        to DNo. These values may be read by the master to prove if the slave is
        in the desired event.
        """
        packet = self.pack(serno,0x20,0x03)
        if not comm:
            packet = self.unpack(packet)
            print(packet['header'])
            print(packet['data'])
            event = 0x82
        else:
            response = comm.talk(packet)
            packet = self.unpack(response)
            event = self._hexhex(packet['data'][0:2])
        return event
    
    def set_APT_Event(self,serno,event,comm=None):
        """ Command to switch the operation mode of the module.
        
        The parameter Event is used to control the slave to fulfil the
        different events. They are:
        
        Normal Measure              VNo: 0x00,  DNo: 0x80
        TDR Scan                    VNo: 0x01,  DNo: 0x81
        Analog Out                  VNo: 0x02,  DNo: 0x82
        ASIC                        VNo: 0x03,  DNo: 0x83
        Temperature Compensation    VNo: 0x04,  DNo: 0x84
        Self Test                   VNo: 0x05,  DNo: 0x85
        MatTempSensor               VNo: 0x06,  DNo: 0x86
        
        When the master sets the slave to above mentioned events, the respective
        value number (VNo) should be sent. If the slave has changed the event
        from the present one to desired one, the respective values will be set
        to DNo. These values may be read by the master to prove if the slave is
        in the desired event.
        """
        if event not in range(0x00,0x06):
            raise CommandsError('Event number not valide!')
            
        packet = self.pack(serno,0x21,0x03,event)
        if not comm:
            packet = self.unpack(packet)
            done = event + 0x80
            while not event == done:
                event = self.get_APT_Event(serno,comm)
            print(packet['header'])
            print(packet['data'])
            state = True
        else:
            response = comm.talk(packet)
            packet = self.unpack(response)
            done = event + 0x80
            while not event == done:
                event = self.get_APT_Event(serno,comm)
            state = True
        return state
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()
