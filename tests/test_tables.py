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
from implib2.imp_tables import Tables, TablesError
from implib2.imp_tables import Table, TableError


# pylint: disable=C0103
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


class TestTables(object):

    def setup(self):
        with open('tests/test_tables.json') as js:
            self.j = json.load(js)
        self.t = Tables()

    def test_Tables(self):
        assert type(self.t) ==  Tables

    def test_GetUnknownTable(self):
        with pytest.raises(TablesError) as e:
            self.t.get('UNKNOWN_TABLE')
        assert e.value.message == "Unknown table: UNKNOWN_TABLE!"

    def test_GetTable(self, table):
        table_a = Table(self.j[table]["Table"], 0, 0)
        table_b = self.t.get(table)
        assert table_a._tbl == table_b._tbl

    def test_GetTableUnknownParameter(self):
        with pytest.raises(TablesError) as e:
            param_table = self.t.get('SYSTEM_PARAMETER', 'UNKNOWN_PARAM')
        assert e.value.message == "Unknown param: UNKNOWN_PARAM!"

    def test_GetTableParam(self, table, param):
        param_table = self.t.get(table, param)
        assert param_table._tbl == self.j[table]['Table'][param]


class TestTable(object):

    def setup(self):
        self.t = Tables()
        self.d = {
            0x00: '{0}B', #  8-bit unsigned char
            0x01: '{0}b', #  8-bit signed char
            0x02: '{0}H', # 16-bit unsigned short
            0x03: '{0}h', # 16-bit signed short
            0x04: '{0}I', # 32-bit unsigned integer
            0x05: '{0}i', # 32-bit signed integer
            0x06: '{0}f', # 32-bit float
            0x07: '{0}d'} # 64-bit double

    def test_Table(self, table):
        param_table = self.t.get(table)

    def test_TableParam(self, table, param):
        param_table = self.t.get(table, param)

    def test_TableGet(self, table):
        param_table = self.t.get(table)
        assert isinstance(param_table.get, int)
        assert param_table.get == self.t._tables[table]["Get"]

    def test_TableParamGet(self, table, param):
        param_table = self.t.get(table, param)
        assert isinstance(param_table.get, int)
        assert param_table.get == self.t._tables[table]["Get"]

    def test_TableSet(self, table):
        param_table = self.t.get(table)
        assert isinstance(param_table.set, int)
        assert param_table.set == self.t._tables[table]["Set"]

    def test_TableParamSet(self, table, param):
        param_table = self.t.get(table, param)
        assert isinstance(param_table.set, int)
        assert param_table.set == self.t._tables[table]["Set"]

    def test_TableCmd(self, table):
        param_table = self.t.get(table)
        assert isinstance(param_table.cmd, int)
        assert param_table.cmd == 255

    def test_TableParamCmd(self, table, param):
        param_table = self.t.get(table, param)
        assert isinstance(param_table.cmd, int)
        assert param_table.cmd == self.t._tables[table]["Table"][param]['No']

    def test_TableFmt(self, table):
        param_table = self.t.get(table)

        expected = '<' # little-endian
        # First make something sortable!
        stable = self.t._tables[table]["Table"]
        format_list = [(stable[param]['No'],
                        stable[param]['Type'],
                        stable[param]['Length']) for param in stable]
        # Second iterate over this thing, sorted by 'No'
        for param in sorted(format_list, key=lambda param: param[0]):
            if param[0] > 250:
                    continue
            format = self.d[param[1] % 0x80]
            length = param[2] / struct.calcsize('<' + format.format(1))
            expected += format.format(length)
        
        assert isinstance(param_table.fmt, str)
        assert param_table.fmt == expected + '1'

    def test_SYSTEM_PARAMETER_TableFmt(self):
        param_table = self.t.get('SYSTEM_PARAMETER')
        expected = '<1I1f1f1H16B1H1B1B'
        assert param_table.fmt == expected

    def test_TableParamFmt(self, table, param):
        param_table = self.t.get(table, param)

        dtable = self.t._tables[table]["Table"][param]
        expected = '<' # little-endian
        format = self.d[dtable['Type'] % 0x80]
        length = dtable['Length'] / struct.calcsize('<' + format.format(1))
        expected += format.format(length)
        
        assert isinstance(param_table.fmt, str)
        assert param_table.fmt == expected