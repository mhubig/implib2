#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2006-2009, Thomas Pircher <tehpeh@gmx.net>
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

from binascii import unhexlify

class CRC(object):
    """
    Class to compute the dallas-1-wire crc of a given hexstring.
    Uses a table driven implementation of the crc algorithm.
    The used CRC polynom is x⁸*x⁵*x⁴*1 or 100110001 or 0x131 or
    (as the most significant bit may be ommitted) 0x31.

    The used table is just a pre-computet list of the polynom
    division of every 256 hex counts with the generator polynom
    0x131.

    The CRC Parametric Model of the dallas-1-wire crc algorithm
    can be defined, in reverence of Ross N. Williams "The Rocksoft
    Model", by these parameters:
    
    Width       = 8bit
    Poly        = 0x131 or 0x31
    ReflectIn   = True
    XorIn       = 0x0
    ReflectOut  = True
    XorOut      = 0x0

    http://www.ross.net/crc/download/crc_v3.txt

    >>> import crc
    >>> crc = crc.CRC()
    >>> crc.calc('FD15ED09')
    'f4'
    """

    def __init__ ( self ):
        self.tbl = self.__maketbl()

    def __reflect ( self, data, width ):
        """ reflect a data word, i.e. reverts the bit order. """
        x = data & 0x01
        for i in range(width - 1):
            data >>= 1
            x = (x << 1) | (data & 0x01)
        return x
     
    def __maketbl( self ):
        tbl = {}
        for i in range(1 << 8):
            register = self.__reflect(i, 8)
            for j in range(8):
                if register & 128 != 0:
                    register = (register << 1) ^ 0x31
                else:
                    register = (register << 1)
            register = self.__reflect(register, 8)
            tbl[i] = register & 255
        return tbl

    def calc ( self, hexstring ):
        tbl = self.tbl
        str = unhexlify(hexstring)
        register = 0x0
        for c in str:
            tblidx   = (register ^ ord(c)) & 0xff
            register = ((register >> 8) ^ tbl[tblidx]) & 255
        return "%02x" % register

    def check ( self, hexstring ):
        data = hexstring[:-2]
        crc  = hexstring[-2:]
        if crc == self.calc(data):
            return True
        else:
            return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()

## <<EOF>>
