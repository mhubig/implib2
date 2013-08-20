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

import os
import pytest
from mock import patch, mock_open, call
from implib2.imp_eeprom import EEPRom


# pylint: disable=C0103,W0212,E1101,W0201
class TestEEPRom(object):

    def setup(self):
        self.epr = EEPRom()

    def test_init(self):
        self.epr._filename = None

    def test_read_ReturnsTrue(self):
        mock = mock_open()
        with patch('__builtin__.open', mock, create=True):
            assert self.epr.read('test.epr')

    def test_read_SetsTheFilename(self):
        mock = mock_open()
        with patch('__builtin__.open', mock, create=True):
            self.epr.read('test.epr')

        assert self.epr._filename == os.path.abspath('implib2/test.epr')

    def test_read_ReadsData(self):
        data = "255\n255\n255"
        mock = mock_open(read_data=data)
        with patch('__builtin__.open', mock, create=True):
            self.epr.read('test.epr')

        assert self.epr.get_page(0) == '\xff\xff\xff'

    def test_read_ReadsDataGetsValueError(self):
        data = "bad"
        mock = mock_open(read_data=data)
        with patch('__builtin__.open', mock, create=True):
            with pytest.raises(ValueError):
                self.epr.read('test.epr')

    def test_read_ReadsDataWithHeader(self):
        header = '; some = header'
        data = "255\n255\n255"
        mock = mock_open(read_data='\n'.join((header, data)))
        with patch('__builtin__.open', mock, create=True):
            self.epr.read('test.epr')

        assert self.epr.get_page(0) == '\xff\xff\xff'
        assert self.epr._header == {'some': 'header'}

    def test_read_ReadsDataWithHeaderAndStuff(self):
        header = '; some = header\n; bla = blub'
        stuff = '; some stuff'
        data = "255\n255\n255"
        mock = mock_open(read_data='\n'.join((header, stuff, data)))
        with patch('__builtin__.open', mock, create=True):
            self.epr.read('test.epr')

        assert self.epr.get_page(0) == '\xff\xff\xff'
        assert self.epr._stuff == ['some stuff']
        assert self.epr._header == {'some': 'header', 'bla': 'blub'}

    def test_set_page_ReturnsTrue(self):
        page = os.urandom(252)
        assert self.epr.set_page(page)

    def test_set_page_StoreFullPageData(self):
        page = os.urandom(252)
        self.epr.set_page(page)
        assert self.epr.get_page(0) == page

    def test_write_ReturnsTrue(self):
        mock = mock_open()
        with patch('__builtin__.open', mock, create=True):
            assert self.epr.write('test.epr')

    def test_write_SomeData(self):
        data = "255\n255\n255"
        self.epr._data.write(data)

        mock = mock_open()
        with patch('__builtin__.open', mock, create=True):
            self.epr.write('test.epr')

        handler = mock()
        handler.write.assert_called_once_with(data)

    def test_write_SomeDataWithHeader(self):
        data = "255\n255\n255"
        header = {'bla': 'blub'}
        self.epr._data.write(data)
        self.epr._header = header

        mock = mock_open()
        with patch('__builtin__.open', mock, create=True):
            self.epr.write('test.epr')

        handler = mock()
        expected = [call('; bla = blub'), call(data)]
        assert handler.write.call_args_list == expected

    def test_write_SomeDataWithHeaderAndStuff(self):
        data = "255\n255\n255"
        header = {'bla': 'blub'}
        stuff = ['test stuff']
        self.epr._data.write(data)
        self.epr._header = header
        self.epr._stuff = stuff

        mock = mock_open()
        with patch('__builtin__.open', mock, create=True):
            self.epr.write('test.epr')

        handler = mock()
        expected = [call('; test stuff'), call('; bla = blub'), call(data)]
        assert handler.write.call_args_list == expected

    def test_pages(self):
        head = os.urandom(252)
        tail = os.urandom(128)
        data = 32 * head + tail
        self.epr._data.write(data)

        assert self.epr.pages == 33
        assert self.epr.get_page(32) == tail

    def test_length(self):
        head = os.urandom(252)
        tail = os.urandom(128)
        data = 32 * head + tail
        self.epr._data.write(data)

        assert self.epr.length == 8192

    def test_iter(self):
        part = os.urandom(252)
        data = 32 * part
        self.epr._data.write(data)

        page_nrs = list()
        for nr, page in self.epr:
            assert page == part
            page_nrs.append(nr)

        assert page_nrs == range(0, 32)
