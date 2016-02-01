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
import os
import json
import pytest
from implib2.imp_helper import _normalize, _load_json, _flp2

TESTS = {
    1:        0b0000000000000000000000001,  # 2**0
    2:        0b0000000000000000000000010,  # 2**1
    3:        0b0000000000000000000000010,  # 2**1
    4:        0b0000000000000000000000100,  # 2**2
    7:        0b0000000000000000000000100,  # 2**2
    8:        0b0000000000000000000001000,  # 2**3
    15:       0b0000000000000000000001000,  # 2**3
    16:       0b0000000000000000000010000,  # 2**4
    31:       0b0000000000000000000010000,  # 2**4
    32:       0b0000000000000000000100000,  # 2**5
    63:       0b0000000000000000000100000,  # 2**5
    64:       0b0000000000000000001000000,  # 2**6
    127:      0b0000000000000000001000000,  # 2**6
    128:      0b0000000000000000010000000,  # 2**7
    255:      0b0000000000000000010000000,  # 2**7
    256:      0b0000000000000000100000000,  # 2**8
    511:      0b0000000000000000100000000,  # 2**8
    512:      0b0000000000000001000000000,  # 2**9
    1023:     0b0000000000000001000000000,  # 2**9
    1024:     0b0000000000000010000000000,  # 2**10
    2047:     0b0000000000000010000000000,  # 2**10
    2048:     0b0000000000000100000000000,  # 2**11
    4095:     0b0000000000000100000000000,  # 2**11
    4096:     0b0000000000001000000000000,  # 2**12
    8191:     0b0000000000001000000000000,  # 2**12
    8192:     0b0000000000010000000000000,  # 2**13
    16383:    0b0000000000010000000000000,  # 2**13
    16384:    0b0000000000100000000000000,  # 2**14
    32767:    0b0000000000100000000000000,  # 2**14
    32768:    0b0000000001000000000000000,  # 2**15
    65535:    0b0000000001000000000000000,  # 2**15
    65536:    0b0000000010000000000000000,  # 2**16
    131071:   0b0000000010000000000000000,  # 2**16
    131072:   0b0000000100000000000000000,  # 2**17
    262143:   0b0000000100000000000000000,  # 2**17
    262144:   0b0000001000000000000000000,  # 2**18
    524287:   0b0000001000000000000000000,  # 2**18
    524288:   0b0000010000000000000000000,  # 2**19
    1048575:  0b0000010000000000000000000,  # 2**19
    1048576:  0b0000100000000000000000000,  # 2**20
    2097151:  0b0000100000000000000000000,  # 2**20
    2097152:  0b0001000000000000000000000,  # 2**21
    4194303:  0b0001000000000000000000000,  # 2**21
    4194304:  0b0010000000000000000000000,  # 2**22
    8388607:  0b0010000000000000000000000,  # 2**22
    8388608:  0b0100000000000000000000000,  # 2**23
    16777215: 0b0100000000000000000000000,  # 2**23
    16777216: 0b1000000000000000000000000}  # 2**24


def test_normalize():
    filename = os.path.abspath('implib2/imp_helper.py')
    assert _normalize(filename) == filename


def test_load_json():
    filename = os.path.abspath('implib2/imp_tables.json')
    with open(filename) as js_file:
        jsdict = json.load(js_file)
    assert _load_json('imp_tables.json') == jsdict


@pytest.mark.parametrize("test", TESTS.items())
def test_flp2(test):
    number, floor = test
    assert _flp2(number) == floor
