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
from implib2.imp_tables import Tables, TablesError


def pytest_generate_tests(metafunc):
    if 'table' in metafunc.fixturenames:
        with open('tests/test_tables.json') as tables_file:
            tables = json.load(tables_file)

        tests = []
        for table in tables:
            for param in tables[table]:
                tests.append((table, param))

        metafunc.parametrize(("table", "param"), tests)


# pylint: disable=invalid-name, protected-access, attribute-defined-outside-init
class TestTables(object):

    def setup(self):
        with open('tests/test_tables.json') as js:
            self.j = json.load(js)
        self.t = Tables()

    def test_load_json(self):
        assert self.t._tables == self.j

    def test_load_json_no_file(self):
        # pylint: disable=no-self-use
        with pytest.raises(IOError):
            Tables('dont_exists.json')

    def test_load_json_falty_file(self):
        # pylint: disable=no-self-use
        with pytest.raises(ValueError):
            Tables('imp_tables.py')

    def test_lookup_unknown_table(self):
        with pytest.raises(TablesError) as e:
            self.t.lookup('UNKNOWN_TABLE', 'UNKNOWN_PARAM')
        assert e.value.message == "Unknown param or table: UNKNOWN_TABLE!"

    def test_lookup_unknown_param(self):
        with pytest.raises(TablesError) as e:
            self.t.lookup('DEVICE_CALIBRATION_PARAMETER_TABLE',
                          'UNKNOWN_PARAM')
        assert e.value.message == "Unknown param or table: UNKNOWN_PARAM!"

    def test_lookup_value(self, table, param):
        row = self.j[table][param]
        value = self.t.lookup(table, param)
        if param == 'Table':
            assert len(row), len(value)
        else:
            assert len(row) + 2, len(value)

    def test_lookup_value_has_get(self, table, param):
        row = self.t.lookup(table, param)
        assert 'Get' in row

    def test_lookup_value_has_set(self, table, param):
        row = self.t.lookup(table, param)
        assert 'Set' in row
