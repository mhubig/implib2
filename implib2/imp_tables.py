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


class ParamTableFactoryError(Exception):
    pass


class ParamTableFactory(object):

    def __init__(self, filename='imp_tables.json'):
        self._tables = _load_json(filename)
        self._invalid = ["ConfigID", "TableSize",
            "DataSize", "GetParam", "GetData"]

    def get(self, table, param=None):        
        name = table

        try:
            group = self._tables[table]
            table = group["Table"]
            set_command = group["Set"]
            get_command = group["Get"]
        except KeyError as e:
            raise ParamTableFactoryError(
                "Unknown table: {}!".format(e.message))

        try:
            params = []
            if param:
                params.append(Param(param, table[param]["No"],
                    table[param]["Type"], table[param]["Status"],
                    table[param]["Length"]))
            else:
                for param in table:
                    if param in self._invalid:
                        continue
                    params.append(Param(param, table[param]["No"],
                        table[param]["Type"], table[param]["Status"],
                        table[param]["Length"]))

        except KeyError as e:
            raise ParamTableFactoryError(
                "Unknown param: {}!".format(e.message))

        return Table(name, get_command, set_command, params)


class Table(object):

    def __init__(self, name, get_command, set_command, params):
        self._name = name
        self._get = get_command
        self._set = set_command
        self._params = sorted(params, key= lambda param: param.cmd)

    def __repr__(self):
        return "Table('{0}', {1}, {2}, {3})".format(
            self._name, self._get, self._set, self._params)

    def __str__(self):
        return self.name

    def __iter__(self):
        for param in self._params:
            yield param

    @property
    def name(self):
        return self._name

    @property
    def get(self):
        return self._get

    @property
    def set(self):
        return self._set

    @property
    def cmd(self):
        if not len(self._params) == 1:
            return 255
        return self._params[0].cmd

class Param(object):

    def __init__(self, name, cmd, fmt, rw, length):
        self._name = name
        self._cmd  = cmd
        self._fmt  = fmt
        self._rw   = rw
        self._len  = length
        self._dtypes = {
            0x00: '{0}B', #  8-bit unsigned char
            0x01: '{0}b', #  8-bit signed char
            0x02: '{0}H', # 16-bit unsigned short
            0x03: '{0}h', # 16-bit signed short
            0x04: '{0}I', # 32-bit unsigned integer
            0x05: '{0}i', # 32-bit signed integer
            0x06: '{0}f', # 32-bit float
            0x07: '{0}d', # 64-bit double
            0x80: '{0}s', #  8-bit unsigned char array
            0x81: '{0}b', #  8-bit signed char array
            0x82: '{0}H', # 16-bit unsigned short array
            0x83: '{0}h', # 16-bit signed short array
            0x84: '{0}I', # 32-bit unsigned integer array
            0x85: '{0}i', # 32-bit signed integer array
            0x86: '{0}f', # 32-bit float array
            0x87: '{0}d'} # 64-bit double array
    
    def __repr__(self):
        return "Param('{0}', {1}, {2}, '{3}', {4})".format(
            self._name, self._cmd, self._fmt, self._rw, self._len)

    def __str__(self):
        return self.name
    
    @property
    def name(self):
        return self._name

    @property
    def cmd(self):
        return self._cmd

    @property
    def fmt(self):
        format = self._dtypes[self._fmt]
        length = self._len / struct.calcsize('<' + format.format(1))
        return '<' + format.format(length)

    @property
    def len(self):
        return self._len

    @property
    def rw(self):
        return self._rw == 'WR'