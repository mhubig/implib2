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

from binascii import a2b_hex as a2b
from implib2.imp_crc import MaximCRC


# pylint: disable=invalid-name, attribute-defined-outside-init
class TestMaximCRC(object):

    def setup(self):
        self.crc = MaximCRC()

    def test_calc_crc(self):
        crc = a2b('f3')
        assert self.crc.calc_crc(a2b('FD15ED09')) == crc

    def test_check_crc(self):
        data = a2b('FD15ED09f3')
        assert self.crc.check_crc(data)
