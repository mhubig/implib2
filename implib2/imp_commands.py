#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import struct


class CommandError(Exception):
    pass


class Command(object):
    def __init__(self, tables, package, datatypes):
        self.tbl = tables
        self.pkg = package
        self.dts = datatypes

    def get_long_ack(self, serno):
        return self.pkg.pack(serno=serno, cmd=0x02)

    def get_short_ack(self, serno):
        return self.pkg.pack(serno=serno, cmd=0x04)

    def get_range_ack(self, rng):
        return self.pkg.pack(serno=rng, cmd=0x06)

    def get_negative_ack(self):
        return self.pkg.pack(serno=16777215, cmd=0x08)

    def get_parameter(self, serno, table, param):
        cmd = self.tbl.lookup(table, param)
        param_no = struct.pack('<B', cmd['No'])
        param_ad = struct.pack('<B', 0)
        data = param_no + param_ad

        package = self.pkg.pack(serno=serno, cmd=cmd['Get'], data=data)
        return package

    # pylint: disable=too-many-arguments
    def set_parameter(self, serno, table, param, values, ad_param=0):
        cmd = self.tbl.lookup(table, param)
        fmt = self.dts.lookup(cmd['Type'] % 0x80)

        param_no = struct.pack('<B', cmd['No'])
        param_ad = struct.pack('<B', ad_param)
        param = struct.pack(fmt.format(len(values)), *values)
        data = param_no + param_ad + param

        package = self.pkg.pack(serno=serno, cmd=cmd['Set'], data=data)
        return package

    # pylint: disable=too-many-arguments
    def do_tdr_scan(self, serno, scan_start, scan_end, scan_span, scan_count):
        scan_start = struct.pack('<B', scan_start)
        scan_end = struct.pack('<B', scan_end)
        scan_span = struct.pack('<B', scan_span)
        scan_count = struct.pack('<H', scan_count)
        data = scan_start + scan_end + scan_span + scan_count

        package = self.pkg.pack(serno=serno, cmd=0x1e, data=data)
        return package

    def get_epr_page(self, serno, page_nr):
        param_no = struct.pack('<B', 255)
        param_ad = struct.pack('<B', page_nr)
        data = param_no + param_ad

        package = self.pkg.pack(serno=serno, cmd=0x3c, data=data)
        return package

    def set_epr_page(self, serno, page_nr, page):
        if len(page) > 250:
            raise CommandError("Page to big, exeeds 250 Bytes!")

        param_no = struct.pack('<B', 255)
        param_ad = struct.pack('<B', page_nr)
        param = page
        data = param_no + param_ad + param

        package = self.pkg.pack(serno=serno, cmd=0x3d, data=data)
        return package
