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

from binascii import unhexlify as uh

class CRCException(Exception):
    pass

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

    >>> crc = CRC()
    >>> crc.calc_crc('FD15ED09')
    'f3'
    """

    def __init__(self):
        self.DEBUG = False
        self.tbl = self._maketbl()

    def _reflect(self, data, width):
        """ reflect a data word, i.e. reverts the bit order. """
        x = data & 0x01
        for i in range(width - 1):
            data >>= 1
            x = (x << 1) | (data & 0x01)
        return x
     
    def _maketbl(self):
        tbl = {}
        for i in range(1 << 8):
            register = self._reflect(i, 8)
            for j in range(8):
                if register & 128 != 0:
                    register = (register << 1) ^ 0x31
                else:
                    register = (register << 1)
            register = self._reflect(register, 8)
            tbl[i] = register & 255
        return tbl

    def calc_crc(self, hex_string):
        tbl = self.tbl
        str = uh(hex_string)
        register = 0x0
        for c in str:
            tblidx   = (register ^ ord(c)) & 0xff
            register = ((register >> 8) ^ tbl[tblidx]) & 255
        return "%02x" % register

    def check_crc(self, hex_string):
        data = hex_string[:-2]
        crc  = hex_string[-2:]
        if crc == self.calc_crc(data):
            return True
        else:
            return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()
