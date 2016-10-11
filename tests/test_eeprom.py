#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
