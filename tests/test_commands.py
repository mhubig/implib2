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
from binascii import a2b_hex as a2b, b2a_hex as b2a

from implib2.imp_packages import Package
from implib2.imp_tables import ParamTableFactory
from implib2.imp_commands import Command, CommandError


# pylint: disable=C0103,W0201,E1101
class TestCommand(object):

    def setup(self):
        self.tbl = ParamTableFactory()
        self.cmd = Command(Package())

    def test_get_long_ack(self):
        pkg = self.cmd.get_long_ack(31001)
        assert pkg == a2b('fd02001979007b')

    def test_get_short_ack(self):
        pkg = self.cmd.get_short_ack(31001)
        assert pkg == a2b('fd0400197900e7')

    def test_get_range_ack(self):
        pkg = self.cmd.get_range_ack(0b111100000000000000000000)
        assert pkg == a2b('fd06000000f0d0')

    def test_get_negative_ack(self):
        pkg = self.cmd.get_negative_ack()
        assert pkg == a2b('fd0800ffffff60')

    def test_get_parameter(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'

        tbl = self.tbl.get(table, param)
        pkg = self.cmd.get_parameter(serno, tbl)
        assert pkg == a2b('fd0a031a7900290100c4')

    def test_get_table(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'

        tbl = self.tbl.get(table)
        pkg = self.cmd.get_parameter(serno, tbl)
        assert pkg == a2b('fd0a031a790029ff0081')

    def test_set_parameter(self):
        serno = 31002
        table = 'PROBE_CONFIGURATION_PARAMETER'
        param = 'DeviceSerialNum'
        ad_param = 0
        value = 31003

        tbl = self.tbl.get(table, param)
        pkg = self.cmd.set_parameter(serno, tbl, param, value, ad_param)
        assert pkg == a2b('fd11071a79002b0c001b790000b0')

    def test_set_table(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'
        vdict = {'Baudrate': 96,
                 'FWVersion': 1.140303,
                 'HWVersion': 1.14,
                 'ModuleCode': 100,
                 'ModuleInfo1': 0,
                 'ModuleInfo2': 1,
                 'ModuleName': 'Trime Pico',
                 'SerialNum': 33913}
        ad_param = 0

        tbl = self.tbl.get(table)
        pkg = self.cmd.set_table(serno, tbl, vdict, ad_param)
        assert pkg == a2b('fd0b251a79009dff007984000085eb913f' +
                          '73f5913f60005472696d65205069636f00' +
                          '00000000006400000147')

    def test_do_tdr_scan(self):
        pkg = self.cmd.do_tdr_scan(30001, 1, 126, 2, 64)
        assert pkg == a2b('fd1e06317500d3017e024000a4')

    def test_get_epr_page(self):
        pkg = self.cmd.get_epr_page(30001, 0)
        assert pkg == a2b('fd3c0331750029ff0081')

    def test_set_epr_page(self):
        page = [0, 0, 0, 0, 0, 0, 0, 0, 35, 255, 255, 0]
        pkg = self.cmd.set_epr_page(30001, 7, page)
        assert pkg == a2b('fd3d0f317500f6ff07000000000000000023ffff007b')

    def test_set_epr_page_to_big(self):
        page = range(0, 251)
        with pytest.raises(CommandError) as e:
            self.cmd.set_epr_page(30001, 7, page)
        assert e.value.message == "Page to big, exeeds 250 Bytes!"
