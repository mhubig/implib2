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

from implib2.imp_packages import Package
from implib2.imp_tables import ParamTableFactory
from implib2.imp_responces import Responce, ResponceError


# pylint: disable=C0103,E1101,W0201
class TestResponce(object):

    def setup(self):
        self.tbl = ParamTableFactory()
        self.res = Responce(Package())

    def test_get_long_ack(self):
        pkg = a2b('0002001a7900a7')
        assert self.res.get_long_ack(pkg, 31002)

    def test_get_long_ack_WrongSerno(self):
        pkg = a2b('0002001a7900a7')
        with pytest.raises(ResponceError) as e:
            self.res.get_long_ack(pkg, 31003)
        assert e.value.message == "Wrong serno in responce!"

    def test_get_short_ack(self):
        pkg = a2b('24')
        assert self.res.get_short_ack(pkg, 31002)

    def test_get_short_ack_WrongSerno(self):
        pkg = a2b('24')
        with pytest.raises(ResponceError) as e:
            self.res.get_short_ack(pkg, 31003)
        assert e.value.message == "Wrong CRC for serno!"

    def test_get_range_ack(self):
        pkg = a2b('24')
        assert self.res.get_range_ack(pkg)

    def test_get_range_ack_NoResponce(self):
        pkg = a2b('')
        assert not self.res.get_range_ack(pkg)

    def test_get_negative_ack(self):
        pkg = a2b('000805ffffffd91a79000042')
        assert self.res.get_negative_ack(pkg) == 31002

    def test_get_parameter(self):
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        serno = 31002

        pkg = a2b('000a051a7900181a79000042')
        tbl = self.tbl.get(table, param)

        assert self.res.get_parameter(serno, tbl, pkg) == (31002,)

    def test_get_parameter_WrongTable(self):
        table = 'PROBE_CONFIGURATION_PARAMETER'
        param = 'DeviceSerialNum'
        serno = 31002

        pkg = a2b('000a051a7900181a79000042')
        tbl = self.tbl.get(table, param)

        with pytest.raises(ResponceError) as e:
            self.res.get_parameter(serno, tbl, pkg)
        assert e.value.message == "Wrong get command in responce!"

    def test_get_parameter_WrongSerno(self):
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        serno = 31003

        pkg = a2b('000a051a7900181a79000042')
        tbl = self.tbl.get(table, param)

        with pytest.raises(ResponceError) as e:
            self.res.get_parameter(serno, tbl, pkg)
        assert e.value.message == "Wrong serial number in responce!"

    def test_get_table(self):
        table = 'SYSTEM_PARAMETER'
        serno = 31002

        tbl = self.tbl.get(table)
        pkg = a2b('000a221a7900ee' + '1a790000295c8f3f85eb913f6' +
                  '0005472696d6500000000000000000000006400000171')

        # SerialNum:   31002
        # HWVersion:   1.1200000047683716
        # FWVersion:   1.1399999856948853
        # Baudrate:    96
        # ModuleName:  'Trime\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        # ModuleCode:  100
        # ModuleInfo1: 0
        # ModuleInfo2: 1

        expected = (31002, 1.1200000047683716, 1.1399999856948853, 96,
                'Trime\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 100, 0, 1)

        assert self.res.get_table(serno, tbl, pkg) == expected

    def test_get_table_WrongTable(self):
        table = 'PROBE_CONFIGURATION_PARAMETER'
        serno = 31002

        tbl = self.tbl.get(table)
        pkg = a2b('000a221a7900ee' + '1a790000295c8f3f85eb913f6' +
                  '0005472696d6500000000000000000000006400000171')

        with pytest.raises(ResponceError) as e:
            self.res.get_table(serno, tbl, pkg)
        assert e.value.message == "Wrong get command in responce!"

    def test_get_table_WrongSerno(self):
        table = 'SYSTEM_PARAMETER'
        serno = 31003

        tbl = self.tbl.get(table)
        pkg = a2b('000a221a7900ee' + '1a790000295c8f3f85eb913f6' +
                  '0005472696d6500000000000000000000006400000171')

        with pytest.raises(ResponceError) as e:
            self.res.get_table(serno, tbl, pkg)
        assert e.value.message == "Wrong serial number in responce!"

    def test_set_parameter(self):
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        serno = 31002

        pkg = a2b('000b001a790054')
        tbl = self.tbl.get(table, param)

        assert self.res.set_parameter(serno, tbl, pkg)

    def test_set_parameter_WrongTable(self):
        table = 'PROBE_CONFIGURATION_PARAMETER'
        param = 'StepDown'
        serno = 31002

        pkg = a2b('000b001a790054')
        tbl = self.tbl.get(table, param)

        with pytest.raises(ResponceError) as e:
            self.res.set_parameter(serno, tbl, pkg)
        assert e.value.message == "Wrong set command in responce!"

    def test_set_parameter_WrongSerno(self):
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        serno = 31003

        pkg = a2b('000b001a790054')
        tbl = self.tbl.get(table, param)

        with pytest.raises(ResponceError) as e:
            self.res.set_parameter(serno, tbl, pkg)
        assert e.value.message == "Wrong serial number in responce!"

    def test_set_table(self):
        table = 'SYSTEM_PARAMETER'
        serno = 31002

        pkg = a2b('000b001a790054')
        tbl = self.tbl.get(table)

        assert self.res.set_parameter(serno, tbl, pkg)

    def test_set_table_WrongTable(self):
        table = 'PROBE_CONFIGURATION_PARAMETER'
        serno = 31002

        pkg = a2b('000b001a790054')
        tbl = self.tbl.get(table)

        with pytest.raises(ResponceError) as e:
            self.res.set_parameter(serno, tbl, pkg)
        assert e.value.message == "Wrong set command in responce!"

    def test_set_parameter_WrongSerno(self):
        table = 'SYSTEM_PARAMETER'
        serno = 31003

        pkg = a2b('000b001a790054')
        tbl = self.tbl.get(table)

        with pytest.raises(ResponceError) as e:
            self.res.set_parameter(serno, tbl, pkg)
        assert e.value.message == "Wrong serial number in responce!"

    def test_do_tdr_scan(self):
        pkg = a2b('001e0b1a79006e112fc44e3702f3e7fb3dc5')
        point0 = {'tdr': 17, 'time': 1.232423437613761e-05}
        point1 = {'tdr': 2, 'time': 0.12300100177526474}
        dat = self.res.do_tdr_scan(pkg)
        assert (dat[0], dat[1]) == (point0, point1)

    def test_do_tdr_scan_StrangeLength(self):
        pkg = a2b('001e0c1a7900e811112fc44e3702f3e7fb3df5')
        with pytest.raises(ResponceError) as e:
            self.res.do_tdr_scan(pkg)
        assert e.value.message == "Responce package has strange length!"

    def test_get_epr_page(self):
        pkg = a2b('003c0b1a790015112fc44e3702f3e7fb3dc5')
        page = [17, 47, 196, 78, 55, 2, 243, 231, 251, 61]
        assert self.res.get_epr_page(pkg) == page

    def test_set_epr_page(self):
        pkg = a2b('003d001a79004c')
        assert self.res.set_epr_page(pkg)

    def test_set_epr_page_WrongCMD(self):
        pkg = a2b('003e001a790002')
        with pytest.raises(ResponceError) as e:
            self.res.set_epr_page(pkg)
        assert e.value.message == "Responce command doesn't match!"
