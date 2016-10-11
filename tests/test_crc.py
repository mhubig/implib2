#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from binascii import a2b_hex as a2b
from implib2.imp_crc import MaximCRC


# pylint: disable=invalid-name, attribute-defined-outside-init
class TestMaximCRC(object):

    def setup(self):
        self.crc = MaximCRC()

    def test_calc_crc(self):
        crc = a2b('f3')
        assert self.crc.calc_crc(a2b('FD15ED09')) == crc

    def test_check_crc(self):
        data = a2b('FD15ED09f3')
        assert self.crc.check_crc(data)
