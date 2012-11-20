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

import struct
from binascii import b2a_hex as b2a, a2b_hex as a2b

from imp_tables import Tables, TablesError
from imp_packages import Package, PackageError

class CommandError(Exception):
    pass

class Command(object):
    def __init__(self, tables, package):
        self.tbl = tables
        self.pkg = package
        self.data_types = {
            0x00: '<{0}B', #  8-bit unsigned char
            0x01: '<{0}b', #  8-bit signed char
            0x02: '<{0}H', # 16-bit unsigned short
            0x03: '<{0}h', # 16-bit signed short
            0x04: '<{0}I', # 32-bit unsigned integer
            0x05: '<{0}i', # 32-bit signed integer
            0x06: '<{0}f', # 32-bit float
            0x07: '<{0}d'} # 64-bit double

    def get_long_ack(self, serno):
        return self.pkg.pack(serno=serno,cmd=0x02)

    def get_short_ack(self, serno):
        return self.pkg.pack(serno=serno, cmd=0x04)

    def get_range_ack(self, range):
        return self.pkg.pack(serno=range,cmd=0x06)

    def get_negative_ack(self):
        return self.pkg.pack(serno=16777215,cmd=0x08)

    def get_parameter(self, serno, table, param):
        cmd = self.tbl.lookup(table, param)
        param_no = struct.pack('<B', cmd['No'])
        param_ad = struct.pack('<B', 0)
        data = param_no + param_ad

        package = self.pkg.pack(serno=serno,cmd=cmd['Get'],data=data)
        return package

    def set_parameter(self, serno, table, param, values, ad_param=0):
        cmd = self.tbl.lookup(table, param)
        format = self.data_types[cmd['Type'] % 0x80]

        param_no = struct.pack('<B', cmd['No'])
        param_ad = struct.pack('<B', ad_param)
        param = struct.pack(format.format(len(values)), *values)
        data = param_no + param_ad + param

        package = self.pkg.pack(serno=serno,cmd=cmd['Set'],data=data)
        return package

    def do_tdr_scan(self, serno, scan_start, scan_end, scan_span, scan_count):
        scan_start = struct.pack('<B', scan_start)
        scan_end   = struct.pack('<B', scan_end)
        scan_span  = struct.pack('<B', scan_span)
        scan_count = struct.pack('<H', scan_count)
        data = scan_start + scan_end + scan_span + scan_count

        package = self.pkg.pack(serno=serno,cmd=0x1e,data=data)
        return package

    def get_epr_image(self, serno, page_nr):
        param_no = struct.pack('<B', 255)
        param_ad = struct.pack('<B', page_nr)
        data = param_no + param_ad

        package = self.pkg.pack(serno=serno,cmd=0x3c,data=data)
        return package

    def set_epr_image(self, serno, page_nr, page):
        if len(page) > 250:
            raise ModuleCommandError("Page to big, exeeds 250 Bytes!")

        param_no = struct.pack('<B', 255)
        param_ad = struct.pack('<B', page_nr)
        param    = str()

        for byte in page:
            param += struct.pack('<B', byte)

        data = param_no + param_ad + param

        package = self.pkg.pack(serno=serno,cmd=0x3d,data=data)
        return package

