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

from struct import pack
from binascii import b2a_hex as b2a, a2b_hex as a2b

class MaximCRCError(Exception):
    pass

class MaximCRC(object):
    def __init__(self):
        self.DEBUG = False
        self.tbl = self._maketbl()

    def _reflect(self, data, width):
        """ reflect a data word, means reverts the bit order. """
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

    def calc_crc(self, byte_str):
        tbl = self.tbl
        register = 0x0
        for c in byte_str:
            tblidx   = (register ^ ord(c)) & 0xff
            register = ((register >> 8) ^ tbl[tblidx]) & 255
        return pack('>B', register)

    def check_crc(self, byte_str):
        data = byte_str[:-1]
        crc  = byte_str[-1:]
        if not crc == self.calc_crc(data):
            return False
        return True

