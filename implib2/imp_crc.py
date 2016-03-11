#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2013, Markus Hubig <mhubig@imko.de>

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


class MaximCRC(object):
    def __init__(self):
        self.table = make_table()

    def calc_crc(self, byte_str):
        reg = 0x0
        for char in byte_str:
            idx = (reg ^ ord(char)) & 0xff
            reg = ((reg >> 8) ^ self.table[idx]) & 255
        return pack('>B', reg)

    def check_crc(self, byte_str):
        data = byte_str[:-1]
        crc = byte_str[-1:]
        if not crc == self.calc_crc(data):
            return False
        return True


def reflect(data, width):
    """ Ceflect a data word, means revert the bit order. """
    reflected = data & 0x01
    for _ in range(width - 1):
        data >>= 1
        reflected = (reflected << 1) | (data & 0x01)
    return reflected


def make_table():
    """ Create a traslation table for the MaximCRC algorithm"""
    table = {}
    for i in range(1 << 8):
        register = reflect(i, 8)
        for _ in range(8):
            if register & 128 != 0:
                register = (register << 1) ^ 0x31
            else:
                register = (register << 1)
        register = reflect(register, 8)
        table[i] = register & 255
    return table
