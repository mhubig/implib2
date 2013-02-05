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

from nose.tools import ok_, eq_, raises
from implib2.imp_datatypes import DataTypes

class TestDataTypes(object):
    # pylint: disable=C0103
    def setUp(self):
        self._dict = {
                0x00: '<{0}B', #  8-bit unsigned char
                0x01: '<{0}b', #  8-bit signed char
                0x02: '<{0}H', # 16-bit unsigned short
                0x03: '<{0}h', # 16-bit signed short
                0x04: '<{0}I', # 32-bit unsigned integer
                0x05: '<{0}i', # 32-bit signed integer
                0x06: '<{0}f', # 32-bit float
                0x07: '<{0}d'} # 64-bit double
        self.dts = DataTypes()

    def test_in(self):
        for d_nr in self._dict:
            ok_(d_nr in self.dts)

    def test_in_NonExistentKey(self):
        answer = 0x08 in self.dts
        eq_(False, answer)

    def test_lookup(self):
        for d_nr in self._dict:
            eq_(self._dict[d_nr], self.dts.lookup(d_nr))

    @raises(KeyError)
    def test_lookup_NonExistentKey(self):
        self.dts.lookup(0x08)

