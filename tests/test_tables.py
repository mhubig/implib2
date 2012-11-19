#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2012, Markus Hubig <mhubig@imko.de>

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
from nose.tools import ok_, eq_, raises
from implib2.imp_tables import Tables

class TestTables():

    def setUp(self):
        self.t = Tables()
        with open('implib2/imp_tables.json') as js:
            self.j = json.load(js)

    def tearDown(self):
        pass

    def test_load_json(self):
        eq_(self.t._tables, self.j)

    @raises(IOError)
    def test_load_json_no_file(self):
        json = Tables('dont_exists.json')

    @raises(ValueError)
    def test_load_json_falty_file(self):
        json = self.t._load_json('imp_tables.py')

    def test_lookup_value(self):
        table = 'APPLICATION_PARAMETER_TABLE'
        row = 'AverageMode'
        value = self.t.lookup(table, row)
        ok_(len(value), 6)

    def test_lookup_value_hast_set(self):
        table = 'APPLICATION_PARAMETER_TABLE'
        row = 'AverageMode'
        value = self.t.lookup(table, row)
        ok_(value.has_key('Set'))

    def test_lookup_value_hast_get(self):
        table = 'APPLICATION_PARAMETER_TABLE'
        row = 'AverageMode'
        value = self.t.lookup(table, row)
        ok_(value.has_key('Get'))

