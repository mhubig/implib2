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

import pytest

from implib2.imp_crc import MaximCRC
from implib2.imp_packages import Package, PackageError


# pylint: disable=invalid-name, attribute-defined-outside-init
class TestPackage(object):

    def setup(self):
        self.pkg = Package()
        self.crc = MaximCRC()

    def test__pack_head(self):
        # e.g. get_long_ack
        pkg = a2b('fd0200bb81002d')
        assert self.pkg.pack(serno=33211, cmd=2) == pkg

    def test__pack_head_AndData(self):
        # e.g. get_erp_image, page1
        pkg = a2b('fd3c03bb810083ff01df')
        data = a2b('ff01')
        assert self.pkg.pack(serno=33211, cmd=60, data=data) == pkg

    def test__pack_head_WithParamNoAndParamAd(self):
        # e.g get_serno
        pkg = a2b('fd0a03bb81009b0100c4')
        data = a2b('0100')
        assert self.pkg.pack(serno=33211, cmd=10, data=data) == pkg

    def test__pack_head_WithParamNoAndParamAdAndParam(self):
        # e.g. set_serno
        pkg = a2b('fd0b07bb8100580100bb810000fb')
        data = a2b('0100bb810000')
        assert self.pkg.pack(serno=33211, cmd=11, data=data) == pkg

    def test__pack_data_ToLong(self):
        data = '\xff' * 253
        with pytest.raises(PackageError) as e:
            self.pkg.pack(serno=33211, cmd=11, data=data)
        assert e.value.message == "Data block bigger than 252Bytes!"

    def test__unpack_head(self):
        # e.g. responce to probe_module_long(33211)
        data = {'header': {'state': 0, 'cmd': 11, 'length': 0,
                           'serno': 33211}, 'data': None}
        pkg = a2b('000b00bb8100e6')
        assert self.pkg.unpack(pkg) == data

    def test__unpack_head_AndData(self):
        # e.g. responce to get_serial(33211)
        data = {'header': {'state': 0, 'cmd': 10, 'length': 5,
                           'serno': 33211}, 'data': '\xbb\x81\x00\x00'}
        pkg = a2b('000a05bb8100aabb810000cc')
        assert self.pkg.unpack(pkg) == data

    def test__unpack_data_ToLong(self):
        data = '\xff' * 253
        crc = self.crc.calc_crc(data)
        pkg = a2b('fd3cffbb8100e0') + data + crc
        with pytest.raises(PackageError) as e:
            self.pkg.unpack(pkg)
        assert e.value.message == "Data block bigger than 252Bytes!"

    def test__unpack_data_FaultyCRC(self):
        data = '\xff' * 252
        pkg = a2b('fd3cffbb8100e0') + data + '\xff'
        with pytest.raises(PackageError) as e:
            self.pkg.unpack(pkg)
        assert e.value.message == "Package with faulty data CRC!"

    def test__unpack_head_FaultyCRC(self):
        data = '\xff' * 252
        crc = self.crc.calc_crc(data)
        pkg = a2b('fd3cffbb8100f0') + data + crc
        with pytest.raises(PackageError) as e:
            self.pkg.unpack(pkg)
        assert e.value.message == "Package with faulty header CRC!"

    def test__unpack_head_WithProbeErrorState(self):
        data = '\xff' * 252
        crc = self.crc.calc_crc(data)
        pkg = a2b('853cffbb8100d9') + data + crc
        with pytest.raises(PackageError) as e:
            self.pkg.unpack(pkg)
        assert e.value.message == "actual moisture is too small in DAC"
