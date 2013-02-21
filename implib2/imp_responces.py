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
from cStringIO import StringIO


class ResponceError(Exception):
    pass


class Responce(object):

    def __init__(self, package):
        self.pkg = package

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
        # pylint: disable=R0201
        return len(packet) == 1

    def get_negative_ack(self, packet):
        responce = self.pkg.unpack(packet)
        return struct.unpack('<I', responce['data'])[0]

    def get_parameter(self, serno, table, bytes_recv):
        responce = self.pkg.unpack(bytes_recv)

        if not responce['header']['cmd'] == table.get:
            raise ResponceError("Wrong get command in responce!")
        if not serno == responce['header']['serno']:
            raise ResponceError("Wrong serial number in responce!")

        data = StringIO(responce['data'])

        param = table.params[0]
        return {param.name: struct.unpack(param.fmt, data.read(param.len))[0]}


    def get_table(self, serno, table, bytes_recv):
        responce = self.pkg.unpack(bytes_recv)

        if not responce['header']['cmd'] == table.get:
            raise ResponceError("Wrong get command in responce!")
        if not serno == responce['header']['serno']:
            raise ResponceError("Wrong serial number in responce!")

        data = StringIO(responce['data'])
        result = {}

        for param in table:
            format = param.fmt
            length = param.len
            name = param.name
            result[name] = struct.unpack(format, data.read(length))[0]

        return result

    def set_parameter(self, serno, table, bytes_recv):
        responce = self.pkg.unpack(bytes_recv)
        command = responce['header']['cmd']

        if not command == table.set:
            raise ResponceError("Wrong set command in responce!")
        if not serno == responce['header']['serno']:
            raise ResponceError("Wrong serial number in responce!")

        return True

    def set_table(self, serno, table, bytes_recv):
        return self.set_parameter(serno, table, bytes_recv)

    def do_tdr_scan(self, packet):
        data = self.pkg.unpack(packet)['data']
        data = [data[i:i+5] for i in range(0, len(data), 5)]
        scan = {}

        for point, tuble in enumerate(data):
            if not len(tuble) == 5:
                raise ResponceError("Responce package has strange length!")
            scan_point         = {}
            scan_point['tdr']  = struct.unpack('<B', tuble[0])[0]
            scan_point['time'] = struct.unpack('<f', tuble[1:5])[0]
            scan[point]        = scan_point

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
