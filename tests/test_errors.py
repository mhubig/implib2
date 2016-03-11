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
from implib2.imp_errors import Errors, ErrorsError


def pytest_generate_tests(metafunc):
    if 'errno' in metafunc.fixturenames:
        with open('tests/test_errors.json') as error_file:
            errors = json.load(error_file)
        metafunc.parametrize("errno", [errno for errno in errors])


# pylint: disable=protected-access, invalid-name, attribute-defined-outside-init
class TestErrors(object):

    def setup(self):
        with open('tests/test_errors.json') as js:
            self.j = json.load(js)
        self.e = Errors()

    def test_load_json(self):
        assert self.e._errors == self.j

    # pylint: disable=no-self-use
    def test_load_json_no_file(self):
        with pytest.raises(IOError):
            Errors('dont_exists.json')

    # pylint: disable=no-self-use
    def test_load_json_falty_file(self):
        with pytest.raises(ValueError):
            Errors('imp_errors.py')

    def test_lookup_unknown_errno(self):
        with pytest.raises(ErrorsError) as e:
            self.e.lookup(666)
        assert e.value.message == "Unknown error number: 666"

    def test_lookup_error(self, errno):
        err = self.j[str(errno)]
        msg = self.e.lookup(errno)

        assert err == msg
