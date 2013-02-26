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

import json
import pytest
import struct
from implib2.imp_tables import ParamTableFactoryError
from implib2.imp_tables import ParamTableFactory, Table, Param

def pytest_generate_tests(metafunc):
    if 'table' in metafunc.fixturenames:

        with open('tests/test_tables.json') as js:
            j = json.load(js)

        if 'param' in metafunc.fixturenames:

            tests = []
            for table in j:
                for param in j[table]['Table']:
                    tests.append((table, param))

            print tests
            metafunc.parametrize(("table", "param"), tests)

        else:
            metafunc.parametrize("table", [table for table in j])


class TestParamTableFactory(object):

    def setup(self):
        with open('tests/test_tables.json') as js:
            self.j = json.load(js)
        self.t = ParamTableFactory()
        self._invalid = ["ConfigID", "TableSize",
            "DataSize", "GetParam", "GetData"]

    def test_ParamTableFactory(self):
        assert type(self.t) == ParamTableFactory

    def test_GetUnknownTable(self):
        with pytest.raises(ParamTableFactoryError) as e:
            self.t.get('UNKNOWN_TABLE')
        assert e.value.message == "Unknown table: UNKNOWN_TABLE!"

    def test_GetTable(self, table):
        json_table = self.j[table]

        param_list = []
        for param in json_table["Table"]:
            if param in self._invalid:
                continue
            json_param = self.j[table]["Table"][param]
            param_list.append(Param(param,
                json_param["No"],
                json_param["Type"],
                json_param["Status"],
                json_param["Length"]))

        param_list.sort(key=lambda p: p.cmd)

        table_a = Table(table, json_table['Get'],
            json_table['Set'],param_list)
        table_b = self.t.get(table)

        assert table_a.name == table_b.name
        assert table_a.get == table_b.get
        assert table_a.set == table_b.set
        assert table_a.cmd == table_b.cmd
        assert repr(table_a) == repr(table_b)

        assert table_b.name == table
        assert table_b.get == json_table["Get"]
        assert table_b.set == json_table["Set"]
        assert table_b.cmd == 255

    def test_GetTableUnknownParameter(self):
        with pytest.raises(ParamTableFactoryError) as e:
            param_table = self.t.get('SYSTEM_PARAMETER', 'UNKNOWN_PARAM')
        assert e.value.message == "Unknown param: UNKNOWN_PARAM!"

    def test_GetTableParam(self, table, param):
        json_table = self.j[table]
        json_param = self.j[table]["Table"][param]

        param_list = [Param(param,
            json_param["No"],
            json_param["Type"],
            json_param["Status"],
            json_param["Length"])]

        table_a = Table(table, json_table['Get'],
            json_table['Set'], param_list)
        table_b = self.t.get(table, param)

        assert table_a.name == table_b.name
        assert table_a.get == table_b.get
        assert table_a.set == table_b.set
        assert table_a.cmd == table_b.cmd
        assert repr(table_a) == repr(table_b)

        assert table_b.name == table
        assert table_b.get == json_table["Get"]
        assert table_b.set == json_table["Set"]
        assert table_b.cmd == json_param["No"]


class TestTable(object):

    def setup(self):
        self.table = Table('TestTable', 1, 2,
            [Param('Testparam', 1, 0x80, 'OR', 3)])

    def test_TableName(self):
        assert self.table.name == 'TestTable'

    def test_TableGet(self):
        assert self.table.get == 1

    def test_TableSet(self):
        assert self.table.set == 2

    def test_TableCmd(self):
        assert self.table.cmd == 1

    def test_TableItems(self):
        assert self.table.items == 1

    def test_TableStr(self):
        assert str(self.table) == 'TestTable'

    def test_TableRepr(self):
        s = "Table('TestTable', 1, 2, [Param('Testparam', 1, 128, 'OR', 3)])"
        assert repr(self.table) == s

    def test_TableIterableAndSortedByCmd(self):
        table = Table('TestTable', 1, 2,
            [Param('TestParam2', 2, 0x80, 'OR', 3),
             Param('TestParam0', 3, 0x80, 'OR', 3),
             Param('TestParam1', 1, 0x80, 'OR', 3)])

        expected = ['TestParam1', 'TestParam2', 'TestParam0']
        for no, param in enumerate(table):
            assert param.name == expected[no]


class TestParam(object):

    def setup(self):
        self.param = Param('TestParam', 1, 0x80, 'OR', 16)
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

    def test_ParamName(self):
        assert self.param.name == 'TestParam'

    def test_ParamCmd(self):
        assert self.param.cmd == 1

    @pytest.mark.parametrize('fmt',
        [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
         0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87])
    def test_ParamFmt(self, fmt):
        param = Param('TestParam', 1, fmt, 'OR', 16)
        string = self._dtypes[fmt]
        length = struct.calcsize(string.format(1))
        assert param.fmt == string.format(16/length)

    def test_ParamLen(self):
        assert self.param.len == 16

    def test_ParamRw(self):
        assert not self.param.rw

    def test_ParamStr(self):
        assert str(self.param) == 'TestParam'

    def test_ParamRepr(self):
        s = "Param('TestParam', 1, 128, 'OR', 16)"
        assert repr(self.param) == s
