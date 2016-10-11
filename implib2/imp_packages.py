#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
