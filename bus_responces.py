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

from imp_packets import Packets, PacketsException

class BusResponcesException(Exception):
    pass

class BusResponces(Packets):
    def __init__(self):
        Packets.__init__(self)
        
    def get_long_ack(self,packet,serno):
        responce = self.unpack(packet)
        return responce['serno']
        
    def get_short_ack(self,packet,serno):
        # not a standart responce packet, just the CRC of the serial
        pass
        
    def get_range_ack(self,packet):
        # not a standart responce packet, just the CRC of the serial
        pass
        
    def get_negative_ack(self, packet):
        responce = self.unpack(packet)
        responce = self._reflect_bytes(responce['data'][0:6])
        return int(responce, 16)
        
    def set_parameter(self, packet):
        responce = self.unpack(packet)
        return responce['serno'], responce['cmd']
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
