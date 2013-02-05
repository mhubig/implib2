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
from nose.tools import eq_, raises
from implib2.imp_errors import Errors, ErrorsError

class TestErrors(object):
    # pylint: disable=C0103,W0212

    def __init__(self):
        with open('tests/test_errors.json') as js:
            self.j = json.load(js)
        self.e = Errors()

    def test_load_json(self):
        eq_(self.e._errors, self.j)

    @raises(IOError)
    def test_load_json_no_file(self):
        # pylint: disable=R0201
        Errors('dont_exists.json')

    @raises(ValueError)
    def test_load_json_falty_file(self):
        # pylint: disable=R0201
        Errors('imp_errors.py')

    @raises(ErrorsError)
    def test_lookup_unknown_errno(self):
        self.e.lookup(666)

    def _lookup_error(self, errno):
        err = self.j[str(errno)]
        msg = self.e.lookup(errno)
        eq_(err, msg)

    def test_lookup_error(self):
        for errno in self.j:
            yield self._lookup_error, int(errno)

