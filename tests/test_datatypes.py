#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pytest
from implib2.imp_datatypes import DataTypes


# pylint: disable=invalid-name, attribute-defined-outside-init
class TestDataTypes(object):

    def setup(self):
        self._dict = {
            0x00: '<{0}B',  # 08-bit unsigned char
            0x01: '<{0}b',  # 08-bit signed char
            0x02: '<{0}H',  # 16-bit unsigned short
            0x03: '<{0}h',  # 16-bit signed short
            0x04: '<{0}I',  # 32-bit unsigned integer
            0x05: '<{0}i',  # 32-bit signed integer
            0x06: '<{0}f',  # 32-bit float
            0x07: '<{0}d'}  # 64-bit double
        self.dts = DataTypes()

    def test_in(self):
        for d_nr in self._dict:
            assert d_nr in self.dts

    def test_in_NonExistentKey(self):
        answer = 0x08 in self.dts
        assert not answer

    def test_lookup(self):
        for d_nr in self._dict:
            assert self._dict[d_nr] == self.dts.lookup(d_nr)

    def test_lookup_NonExistentKey(self):
        with pytest.raises(KeyError):
            self.dts.lookup(0x08)
