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

import os
import pytest
from mock import patch, call, MagicMock, PropertyMock
from implib2.imp_modules import Module, ModuleError


# pylint: disable=C0103,W0212,R0904,E1101,W0201
class TestModule(object):
    def setup(self):
        self.serno = 31002
        self.bus = MagicMock()
        self.mod = Module(self.bus, self.serno)

    ###########################
    ## Read only Properties  ##
    ###########################

    def test_serno(self):
        param = 'SerialNum'
        value = self.serno
        self.bus.get.return_value = {param: value}
        assert self.mod.serno == value

    def test_name(self):
        param = 'ModuleName'
        value = 'Trime Pico\x00\x00\x00\x00\x00\x00'
        self.bus.get.return_value = {param: value}
        assert self.mod.name == value.split('\x00')[0]

    def test_code(self):
        param = 'ModuleCode'
        value = 100
        self.bus.get.return_value = {param: value}
        assert self.mod.code == value

    def test_info1(self):
        param = 'Info1'
        value = 0
        self.bus.get.return_value = {param: value}
        assert self.mod.info1 == value

    def test_info2(self):
        param = 'Info2'
        value = 1
        self.bus.get.return_value = {param: value}
        assert self.mod.info2 == value

    def test_hw_version(self):
        param = 'HWVersion'
        value = 1.1399999856948853
        self.bus.get.return_value = {param: value}
        assert self.mod.hw_version == 1.14

    def test_fw_version(self):
        param = 'FWVersion'
        value = 1.14030300000000002
        self.bus.get.return_value = {param: value}
        assert self.mod.fw_version == 1.140303

    ###########################
    ## Writeable Properties  ##
    ###########################

    @pytest.mark.parametrize("mode", [(0, 'A'), (1, 'B'), (2, 'C')])
    def test_measure_mode_Get(self, mode):
        param = 'MeasMode'
        value = mode[0]
        self.bus.get.return_value = {param: value}
        assert self.mod.measure_mode == mode[1]

    def test_measure_mode_GetBadMode(self):
        param = 'MeasMode'
        value = 3
        self.bus.get.return_value = {param: value}
        with pytest.raises(ModuleError) as e:
            self.mod.measure_mode
        assert e.value.message == "Unknown measure mode!"

    @pytest.mark.parametrize("mode", [(0, 'A'), (1, 'B'), (2, 'C')])
    def test_measure_mode_Set(self, mode):

        expected = [call()]

        with patch('implib2.imp_modules.Module._event_mode',
                new_callable=PropertyMock) as mock_event_mode:
            mock_event_mode.return_value = "NormalMeasure"
            mod = Module(self.bus, self.serno)
            self.bus.set.return_value = True

            mod.measure_mode = mode[1]
            assert mock_event_mode.mock_calls == expected

    @pytest.mark.parametrize("mode", [(0, 'A'), (1, 'B'), (2, 'C')])
    def test_measure_mode_SetWrongEventMode(self, mode):

        expected = [call(), call("NormalMeasure")]

        with patch('implib2.imp_modules.Module._event_mode',
                new_callable=PropertyMock) as mock_event_mode:
            mock_event_mode.return_value = "SelfTest"
            mod = Module(self.bus, self.serno)
            self.bus.set.return_value = True

            mod.measure_mode = mode[1]
            assert mock_event_mode.mock_calls == expected


    def test_measure_mode_SetBadMode(self):

        expected = "'D' is not a valid measure mode!"

        with patch('implib2.imp_modules.Module._event_mode',
                new_callable=PropertyMock) as mock_event_mode:
            mock_event_mode.return_value = "NormalMeasure"
            mod = Module(self.bus, self.serno)
            self.bus.set.return_value = True

            with pytest.raises(ModuleError) as e:
                mod.measure_mode = 'D'
            assert e.value.message == expected

