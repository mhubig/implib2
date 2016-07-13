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
from .imp_crc import MaximCRC
from .imp_errors import Errors


class PackageError(Exception):
    pass


class Package(object):

    def __init__(self):
        self.crc = MaximCRC()
        self.err = Errors()

    def _pack_data(self, data):
        if len(data) > 252:
            raise PackageError("Data block bigger than 252Bytes!")
        return data + self.crc.calc_crc(data)

    def _unpack_data(self, data):
        if len(data[:-1]) > 252:  # NOTE: crc is still attached
            raise PackageError("Data block bigger than 252Bytes!")
        if not self.crc.check_crc(data):
            raise PackageError("Package with faulty data CRC!")
        return data[:-1]

    def _pack_head(self, cmd, length, serno):
        state = struct.pack('<B', 0xfd)  # indicates IMP232N protocol version
        cmd = struct.pack('<B', cmd)
        length = struct.pack('<B', length)
        serno = struct.pack('<I', serno)[:-1]

        header = state + cmd + length + serno
        header = header + self.crc.calc_crc(header)

        return header

    def _unpack_head(self, header):
        state = struct.unpack('<B', header[0])[0]
        cmd = struct.unpack('<B', header[1])[0]
        length = struct.unpack('<B', header[2])[0]
        serno = struct.unpack('<I', header[3:6] + '\x00')[0]

        if not self.crc.check_crc(header):
            raise PackageError("Package with faulty header CRC!")

        states = [0, 122, 123, 160, 161, 162, 163, 164, 165, 166, 253, 255]
        if state not in states:
            raise PackageError("{0}".format(self.err.lookup(state)))

        return {'state': state, 'cmd': cmd, 'length': length, 'serno': serno}

    def pack(self, serno, cmd, data=None):
        if data:
            data = self._pack_data(data)
            header = self._pack_head(cmd, len(data), serno)
            package = header + data
        else:
            header = self._pack_head(cmd, 0, serno)
            package = header

        return package

    def unpack(self, package):
        header = self._unpack_head(package[:7])
        data = None

        if len(package) > 7:
            data = self._unpack_data(package[7:])

        package = {'header': header, 'data': data}

        return package
