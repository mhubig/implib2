#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from binascii import a2b_hex as a2b

import pytest

from implib2.imp_tables import Tables
from implib2.imp_packages import Package
from implib2.imp_datatypes import DataTypes
from implib2.imp_commands import Command, CommandError


# pylint: disable=invalid-name, attribute-defined-outside-init
class TestCommand(object):

    def setup(self):
        self.cmd = Command(Tables(), Package(), DataTypes())

    def test_get_long_ack(self):
        pkg = self.cmd.get_long_ack(31001)
        assert pkg == a2b('fd02001979007b')

    def test_get_short_ack(self):
        pkg = self.cmd.get_short_ack(31001)
        assert pkg == a2b('fd0400197900e7')

    def test_get_range_ack(self):
        pkg = self.cmd.get_range_ack(0b111100000000000000000000)
        assert pkg == a2b('fd06000000f0d0')

    def test_get_negative_ack(self):
        pkg = self.cmd.get_negative_ack()
        assert pkg == a2b('fd0800ffffff60')

    def test_get_parameter(self):
        pkg = self.cmd.get_parameter(31002, 'SYSTEM_PARAMETER_TABLE',
                                     'SerialNum')
        assert pkg == a2b('fd0a031a7900290100c4')

    def test_set_parameter(self):
        pkg = self.cmd.set_parameter(31002,
                                     'PROBE_CONFIGURATION_PARAMETER_TABLE',
                                     'DeviceSerialNum', [31003])
        assert pkg == a2b('fd11071a79002b0c001b790000b0')

    def test_do_tdr_scan(self):
        pkg = self.cmd.do_tdr_scan(30001, 1, 126, 2, 64)
        assert pkg == a2b('fd1e06317500d3017e024000a4')

    def test_get_epr_page(self):
        pkg = self.cmd.get_epr_page(30001, 0)
        assert pkg == a2b('fd3c0331750029ff0081')

    def test_set_epr_page(self):
        page = a2b('000000000000000023ffff00')
        pkg = self.cmd.set_epr_page(30001, 7, page)
        assert pkg == a2b('fd3d0f317500f6ff07000000000000000023ffff007b')

    def test_set_epr_page_to_big(self):
        page = range(0, 251)
        with pytest.raises(CommandError) as e:
            self.cmd.set_epr_page(30001, 7, page)
        assert e.value.message == "Page to big, exeeds 250 Bytes!"
