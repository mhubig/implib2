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
import os
import json
from nose.tools import eq_

from implib2.imp_helper import _normalize, _load_json

def test_normalize():
    filename = os.path.abspath('implib2/imp_helper.py')
    eq_(_normalize(filename), filename)

def test_load_json():
    filename = os.path.abspath('implib2/imp_tables.json')
    with open(filename) as js_file:
        jsdict = json.load(js_file)
    eq_(_load_json('imp_tables.json'), jsdict)

