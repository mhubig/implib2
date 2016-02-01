#!/usr/bin/env python
# encoding: utf-8
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

import io
import mock

from implib2.imp_eeprom import EEPROM


# pylint: disable=no-init, invalid-name, protected-access, no-self-use
class TestEEPROM(object):

    def test_init_ReadsData(self):
        data = io.StringIO(u'255\n255\n255')
        with mock.patch('implib2.imp_eeprom.open', create=True) as mock_open:
            mock_open.return_value = data
            eeprom = EEPROM('test.epr')
        assert eeprom._data.getvalue() == '\xff\xff\xff'

    def test_init_ReadsDataWithHeader(self):
        data = io.StringIO(u'; some = header\n255\n255\n255')
        with mock.patch('implib2.imp_eeprom.open', create=True) as mock_open:
            mock_open.return_value = data
            eeprom = EEPROM('test.epr')

        # pylint: disable=no-member
        assert eeprom._data.getvalue() == '\xff\xff\xff'
        assert eeprom.some == 'header'

    def test_init_ReadsDataWithHeaderHasSpace(self):
        data = io.StringIO(u'; some bla = header\n255\n255\n255')
        with mock.patch('implib2.imp_eeprom.open', create=True) as mock_open:
            mock_open.return_value = data
            eeprom = EEPROM('test.epr')

        # pylint: disable=no-member
        assert eeprom._data.getvalue() == '\xff\xff\xff'
        assert eeprom.some_bla == 'header'

    def test_iterating_OnePage(self):
        data = io.StringIO(u'255\n' * 250)
        with mock.patch('implib2.imp_eeprom.open', create=True) as mock_open:
            mock_open.return_value = data
            eeprom = EEPROM('test.epr')

        for no, page in enumerate(eeprom):
            assert len(page) == 250
            assert page == '\xff' * 250
            assert no == 0

    def test_iterating_TwoAndaHalfePage(self):
        data = io.StringIO(u'255\n' * 625)
        with mock.patch('implib2.imp_eeprom.open', create=True) as mock_open:
            mock_open.return_value = data
            eeprom = EEPROM('test.epr')

        for no, page in enumerate(eeprom):
            assert no in [0, 1, 2]
            if no in [0, 1]:
                assert len(page) == 250
                assert page == '\xff' * 250
            else:
                assert len(page) == 125
                assert page == '\xff' * 125
