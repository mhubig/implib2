#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2012, Markus Hubig <mhubig@imko.de>

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

import os
from nose.tools import eq_, raises
from binascii import a2b_hex as a2b

from implib2.imp_crc import MaximCRC
from implib2.imp_packages import Package, PackageError

class TestPackage(object):
    # pylint: disable=C0103

    def setUp(self):
        self.pkg = Package()
        self.crc = MaximCRC()

    def test_pack_header(self):
        # e.g. get_long_ack
        pkg = a2b('fd0200bb81002d')
        eq_(self.pkg.pack(serno=33211, cmd=2), pkg)

    def test_pack_header_and_data(self):
        # e.g. get_erp_image, page1
        pkg = a2b('fd3c03bb810083ff01df')
        data = a2b('ff01')
        eq_(self.pkg.pack(serno=33211, cmd=60, data=data), pkg)

    def test_pack_header_with_param_no_and_param_ad(self):
        # e.g get_serno
        pkg = a2b('fd0a03bb81009b0100c4')
        data = a2b('0100')
        eq_(self.pkg.pack(serno=33211, cmd=10, data=data), pkg)

    def test_pack_header_with_param_no_and_param_ad_and_param(self):
        # e.g. set_serno
        pkg = a2b('fd0b07bb8100580100bb810000fb')
        data = a2b('0100bb810000')
        eq_(self.pkg.pack(serno=33211, cmd=11, data=data), pkg)

    @raises(PackageError)
    def test_pack_data_to_long(self):
        data = os.urandom(253)+"\xff"
        self.pkg.pack(serno=33211, cmd=11, data=data)

    def test_unpack_header(self):
        # e.g. responce to probe_module_long(33211)
        data = {'header': {'state': 0, 'cmd': 11, 'length': 0, 'serno': 33211},
                'data'  : None}
        pkg = a2b('000b00bb8100e6')
        eq_(self.pkg.unpack(pkg), data)

    def test_unpack_header_and_data(self):
        # e.g. responce to get_serial(33211)
        data = {'header': {'state': 0, 'cmd': 10, 'length': 5, 'serno': 33211},
                'data'  : '\xbb\x81\x00\x00'}
        pkg = a2b('000a05bb8100aabb810000cc')
        eq_(self.pkg.unpack(pkg), data)

    @raises(PackageError)
    def test_unpack_data_to_long(self):
        random = os.urandom(253)
        crc = self.crc.calc_crc(random)
        pkg = a2b('fd3cffbb8100e0') + random + crc
        self.pkg.unpack(pkg)

    @raises(PackageError)
    def test_unpack_data_with_faulty_crc(self):
        random = os.urandom(253)
        pkg = a2b('fd3cffbb8100e0') + random
        self.pkg.unpack(pkg)

    @raises(PackageError)
    def test_unpack_header_with_faulty_crc(self):
        random = os.urandom(252)
        crc = self.crc.calc_crc(random)
        pkg = a2b('fd3cffbb8100f0') + random + crc
        self.pkg.unpack(pkg)

    @raises(PackageError)
    def test_unpack_header_with_probe_error_state(self):
        random = os.urandom(250)
        crc = self.crc.calc_crc(random)
        pkg = a2b('853cffbb8100d9') + random + crc
        self.pkg.unpack(pkg)
