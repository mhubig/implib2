#!/usr/bin/env python
"""
Copyright (C) 2011, Markus Hubig <mhubig@imko.de>

This file is part of IMPLib2.

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

from imp_packets import IMPPackets, IMPPacketsException

class BusResponceException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BusResponce(Packet):
    def __init__(self):
        Packet.__init__(self)
        
    def responce_get_long_acknowledge(self, packet):
        responce = self.unpack(packet)
        return responce['serno']
        
    def responce_get_short_acknowledge(self, packet):
        # not a standart responce packet, just the CRC of the serial
        pass
        
    def responce_get_acknowledge_for_serial_number_range(self, packet):
        # not a standart responce packet, just the CRC of the serial
        pass
        
    def responce_get_negative_acknowledge(self, packet):
        responce = self.unpack(packet)
        return responce['serno']
        
    def responce_get_parameter(self, packet):
        responce = self.unpack(packet)
        return responce['serno'], responce['cmd'], responce['data']
        
    def responce_set_parameter(self, packet):
        responce = self.unpack(packet)
        return responce['serno'], responce['cmd']
        
    def responce_do_tdr_scan(self, packet):
        responce = self.unpack(packet)
        return responce['serno'], responce['cmd'], responce['data']
        
    def responce_get_epr_image(self, packet):
        responce = self.unpack(packet)
        return responce['serno'], responce['cmd'], responce['data']
        
    def responce_set_erp_image(self, packet):
        responce = self.unpack(packet)
        return responce['serno'], responce['cmd']
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
