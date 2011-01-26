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
from packet import Packet, PacketExceptions

class BaseResponceException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BaseResponce(Packet):
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
