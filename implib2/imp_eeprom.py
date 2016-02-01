#!/usr/bin/env python
# encoding: utf-8
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

import io
import re
import struct


# pylint: disable=too-few-public-methods
class EEPROM(object):
    """This Class represents a simple data structure to hold an EEPROM
    image. It can be used with :func:`Module.write_eeprom` to update the
    EEPROM image of the probe.
    """

    def __init__(self, filename):
        self._data = io.BytesIO()
        self._page = 250
        self._regx = re.compile('^; (.*?) = (.*?)$')

        with open(filename) as epr:
            for line in epr:
                if line.startswith(';'):
                    self._readmeta(line)
                else:
                    self._readdata(line)

        self._data.seek(0)

    def __iter__(self):
        while True:
            data = self._data.read(self._page)
            if not data:
                break
            yield data

    def _readdata(self, line):
        byte = struct.pack('>B', int(line.strip()))
        self._data.write(byte)

    def _readmeta(self, line):
        match = self._regx.match(line)
        if match:
            key, value = match.group(1, 2)
            setattr(self, key.replace(' ', '_').strip(), value.strip())
