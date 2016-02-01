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

import struct


class ResponceError(Exception):
    pass


class Responce(object):
    def __init__(self, tables, package, datatypes):
        self.tbl = tables
        self.pkg = package
        self.dts = datatypes

    def get_long_ack(self, packet, serno):
        responce = self.pkg.unpack(packet)

        if not serno == responce['header']['serno']:
            raise ResponceError("Wrong serno in responce!")

        return True

    def get_short_ack(self, packet, serno):
        serno = struct.pack('<I', serno)[:-1]
        res_crc = self.pkg.crc.calc_crc(serno)

        if not res_crc == packet:
            raise ResponceError("Wrong CRC for serno!")

        return True

    def get_range_ack(self, packet):
        # pylint: disable=no-self-use
        return len(packet) == 1

    def get_negative_ack(self, packet):
        responce = self.pkg.unpack(packet)
        return struct.unpack('<I', responce['data'])[0]

    def get_parameter(self, packet, table, param):
        data = self.pkg.unpack(packet)['data']
        cmd = self.tbl.lookup(table, param)

        fmt = self.dts.lookup(cmd['Type'] % 0x80)
        length = len(data)/struct.calcsize(fmt.format(1))

        return struct.unpack(fmt.format(length), data)

    def set_parameter(self, packet, table, serno):
        responce = self.pkg.unpack(packet)
        command = responce['header']['cmd']
        cmd = self.tbl.lookup(table, 'Table')

        if not command == cmd['Set']:
            raise ResponceError("Wrong set command in responce!")
        if not serno == responce['header']['serno']:
            raise ResponceError("Wrong serial number in responce!")

        return True

    def do_tdr_scan(self, packet):
        data = self.pkg.unpack(packet)['data']
        data = [data[i:i+5] for i in range(0, len(data), 5)]
        scan = {}

        for point, tuble in enumerate(data):
            if not len(tuble) == 5:
                raise ResponceError("Responce package has strange length!")
            scan_point = {}
            scan_point['tdr'] = struct.unpack('<B', tuble[0])[0]
            scan_point['time'] = struct.unpack('<f', tuble[1:5])[0]
            scan[point] = scan_point

        return scan

    def get_epr_page(self, packet):
        responce = self.pkg.unpack(packet)
        page = list()

        for byte in responce['data']:
            page.append(struct.unpack('<B', byte)[0])

        return page

    def set_epr_page(self, packet):
        responce = self.pkg.unpack(packet)
        if not responce['header']['cmd'] == 61:
            raise ResponceError("Responce command doesn't match!")
        return True
