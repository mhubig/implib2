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
from .imp_helper import _load_json


class TablesError(Exception):
    pass


class TableError(Exception):
    pass


# pylint: disable=R0903,C0103
class Tables(object):

    def __init__(self, filename='imp_tables.json'):
        self._tables = _load_json(filename)

    def get(self, table, param=False):
        
        try:
            group = self._tables[table]
            tbl_content = group['Table']
            set_command = group["Set"]
            get_command = group["Get"]
        except KeyError as e:
            raise TablesError("Unknown table: {}!".format(e.message))

        try:
            if param: tbl_content = tbl_content[param]
        except KeyError as e:
            raise TablesError("Unknown param: {}!".format(e.message))

        return Table(tbl_content, get_command, set_command)


class Table(object):

    def __init__(self, tbl_content, get_command, set_command):
        self._tbl = tbl_content
        self._get = get_command
        self._set = set_command
        self._dtypes = {
            0x00: '{0}B', #  8-bit unsigned char
            0x01: '{0}b', #  8-bit signed char
            0x02: '{0}H', # 16-bit unsigned short
            0x03: '{0}h', # 16-bit signed short
            0x04: '{0}I', # 32-bit unsigned integer
            0x05: '{0}i', # 32-bit signed integer
            0x06: '{0}f', # 32-bit float
            0x07: '{0}d'} # 64-bit double

    def _get_command_number(self):
        if 'GetData' in self._tbl:
            cmd = self._tbl['GetData']['No']
        else:
            cmd = self._tbl['No']
        return cmd

    def _get_format_string(self):
        result = '<' # little-endian
        if 'GetData' in self._tbl:
            
            # First make something sortable!
            table = [(self._tbl[param]['No'],
                      self._tbl[param]['Type'],
                      self._tbl[param]['Length']) for param in self._tbl]
            
            # Second iterate over this thing, sorted by 'No'
            for param in sorted(table, key=lambda param: param[0]):
                if param[0] > 250:
                    continue
                format = self._dtypes[param[1] % 0x80]
                length = param[2] / struct.calcsize('<' + format.format(1))
                result += format.format(length)
        else:
            param = (self._tbl["No"], self._tbl["Type"], self._tbl["Length"])
            format = self._dtypes[param[1] % 0x80]
            length = param[2] / struct.calcsize('<' + format.format(1))
            result += format.format(length)
        
        return result

    @property
    def get(self):
        return self._get

    @property
    def set(self):
        return self._set

    @property
    def cmd(self):
        return self._get_command_number()

    @property
    def fmt(self):
        return self._get_format_string()