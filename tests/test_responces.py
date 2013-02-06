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

import pytest
from binascii import a2b_hex as a2b
from implib2.imp_tables import Tables
from implib2.imp_packages import Package
from implib2.imp_datatypes import DataTypes
from implib2.imp_responces import Responce, ResponceError

# pylint: disable=C0103,E1101,W0201
class TestResponce(object):

    def setup(self):
        self.res = Responce(Tables(), Package(), DataTypes())

    def test_get_long_ack_right_serno(self):
        pkg = a2b('0002001a7900a7')
        assert self.res.get_long_ack(pkg, 31002)

    def test_get_long_ack_wrong_serno(self):
        pkg = a2b('0002001a7900a7')
        with pytest.raises(ResponceError):
            self.res.get_long_ack(pkg, 31003)

    def test_get_short_ack_right_serno(self):
        pkg = a2b('24')
        assert self.res.get_short_ack(pkg, 31002)

    def test_get_short_ack_wrong_serno(self):
        pkg = a2b('24')
        with pytest.raises(ResponceError):
            self.res.get_short_ack(pkg, 31003)

    def test_get_range_ack_responce(self):
        pkg = a2b('24')
        assert self.res.get_range_ack(pkg)

    def test_get_range_ack_no_responce(self):
        pkg = a2b('')
        assert self.res.get_range_ack(pkg) is False

    def test_get_negative_ack(self):
        pkg = a2b('000805ffffffd91a79000042')
        assert self.res.get_negative_ack(pkg) == 31002

    def test_get_parameter(self):
        pkg   = a2b('000a051a7900181a79000042')
        param = 'SerialNum'
        table = 'SYSTEM_PARAMETER_TABLE'
        assert self.res.get_parameter(pkg, table, param) == (31002,)

    def test_set_parameter(self):
        pkg   = a2b('0011001a790095')
        serno = 31002
        table = 'PROBE_CONFIGURATION_PARAMETER_TABLE'
        assert self.res.set_parameter(pkg, table, serno)

    def test_set_parameter_wrong_table(self):
        pkg = a2b('0011001a790095')
        serno = 31002
        table = 'SYSTEM_PARAMETER_TABLE'
        with pytest.raises(ResponceError):
            self.res.set_parameter(pkg, table, serno)

    def test_set_parameter_wrong_serno(self):
        pkg = a2b('0011001a790095')
        serno = 31003
        table = 'PROBE_CONFIGURATION_PARAMETER_TABLE'
        with pytest.raises(ResponceError):
            self.res.set_parameter(pkg, table, serno)

    def test_do_tdr_scan(self):
        pkg = a2b('001e0b1a79006e112fc44e3702f3e7fb3dc5')
        point0 = {'tdr': 17, 'time': 1.232423437613761e-05}
        point1 = {'tdr': 2, 'time': 0.12300100177526474}
        dat = self.res.do_tdr_scan(pkg)
        assert (dat[0], dat[1]) == (point0, point1)

    def test_do_tdr_scan_strange_length(self):
        pkg = a2b('001e0c1a7900e811112fc44e3702f3e7fb3df5')
        with pytest.raises(ResponceError):
            self.res.do_tdr_scan(pkg)

    def test_get_epr_page(self):
        pkg = a2b('003c0b1a790015112fc44e3702f3e7fb3dc5')
        page = [17, 47, 196, 78, 55, 2, 243, 231, 251, 61]
        assert self.res.get_epr_page(pkg) == page

    def test_set_epr_page(self):
        pkg = a2b('003d001a79004c')
        assert self.res.set_epr_page(pkg)

    def test_set_epr_page_with_wrong_cmd(self):
        pkg = a2b('003e001a790002')
        with pytest.raises(ResponceError):
            self.res.set_epr_page(pkg)

