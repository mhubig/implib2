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

import pytest
from mock import patch, call, MagicMock
from binascii import a2b_hex as a2b

from implib2.imp_bus import Bus, BusError
from implib2.imp_device import Device, DeviceError # pylint: disable=W0611
from implib2.imp_commands import Command           # pylint: disable=W0611
from implib2.imp_responces import Responce         # pylint: disable=W0611
from implib2.imp_tables import ParamTableFactory   # pylint: disable=W0611


# pylint: disable=C0103,R0902,W0201,E1101
class TestBus(object):

    def setup(self):
        self.patcher1 = patch('implib2.imp_bus.Device')
        self.patcher2 = patch('implib2.imp_bus.Command')
        self.patcher3 = patch('implib2.imp_bus.Responce')
        self.patcher4 = patch('implib2.imp_bus.ParamTableFactory')

        mock_dev = self.patcher1.start()
        mock_cmd = self.patcher2.start()
        mock_res = self.patcher3.start()
        mock_tbl = self.patcher4.start()

        self.dev = mock_dev()
        self.cmd = mock_cmd()
        self.res = mock_res()
        self.tbl = mock_tbl()

        self.manager = MagicMock()
        self.manager.attach_mock(self.dev, 'dev')
        self.manager.attach_mock(self.cmd, 'cmd')
        self.manager.attach_mock(self.res, 'res')
        self.manager.attach_mock(self.tbl, 'tbl')

        self.ptf = ParamTableFactory()
        self.bus = Bus()

    def teardown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()

    def test_wakeup(self):
        address  = 16777215
        table    = 'ACTION_PARAMETER'
        param    = 'EnterSleep'
        value    = 0
        ad_param = 0

        tbl = self.ptf.get(table, param)
        pkg = a2b('fd1504fffffffe05000035')

        expected_calls = [
            call.tbl.get(table, param),
            call.cmd.set_parameter(address, tbl, [value]),
            call.dev.write_pkg(pkg),
        ]

        self.tbl.get.return_value = tbl
        self.cmd.set_parameter.return_value = pkg
        self.dev.write_pkg.return_value = True

        assert self.bus.wakeup()
        assert self.manager.mock_calls == expected_calls

    def test_sync(self):
        address  = 16777215
        table    = 'SYSTEM_PARAMETER'
        param    = 'Baudrate'
        baudrate = 9600
        value    = baudrate/100
        ad_param = 0

        tbl = self.ptf.get(table, param)
        pkg = a2b('fd0b05ffffffaf0400600054')

        expected_calls = [
            call.tbl.get(table, param),
            call.cmd.set_parameter(address, tbl, [value]),
            call.dev.close_device(),

            call.dev.open_device(baudrate=1200),
            call.dev.write_pkg(pkg),
            call.dev.close_device(),

            call.dev.open_device(baudrate=2400),
            call.dev.write_pkg(pkg),
            call.dev.close_device(),

            call.dev.open_device(baudrate=4800),
            call.dev.write_pkg(pkg),
            call.dev.close_device(),

            call.dev.open_device(baudrate=9600),
            call.dev.write_pkg(pkg),
            call.dev.close_device(),

            call.dev.open_device(baudrate=baudrate)
        ]

        self.tbl.get.return_value = tbl
        self.cmd.set_parameter.return_value = pkg
        self.dev.write_pkg.return_value = True

        self.bus.sync(baudrate=baudrate)
        assert self.bus.bus_synced
        assert self.manager.mock_calls == expected_calls

    def test_sync_WithWrongBaudrate(self):
        with pytest.raises(BusError) as e:
            self.bus.sync(baudrate=6666)
        assert e.value.message == "Unknown baudrate!"

    def test_scan_AndFindEverything(self):
        minserial = 0b0001 #  1
        maxserial = 0b1010 # 10

        self.bus.probe_range = MagicMock()
        self.bus.probe_range.return_value = True

        self.bus.probe_module_short = MagicMock()
        self.bus.probe_module_short.return_value = True

        range_list = [
                call(0b1000), #  8
                call(0b1100), # 12
                call(0b1110), # 14
                call(0b1111), # 15
                call(0b1101), # 13
                call(0b1010), # 10
                call(0b1011), # 11
                call(0b1001), #  9
                call(0b0100), #  4
                call(0b0110), #  6
                call(0b0111), #  7
                call(0b0101), #  5
                call(0b0010), #  2
                call(0b0011), #  3
                call(0b0001)  #  1
        ]

        modules_list = [
                call(0b1111), # 15
                call(0b1110), # 14
                call(0b1101), # 13
                call(0b1100), # 12
                call(0b1011), # 11
                call(0b1010), # 10
                call(0b1001), #  9
                call(0b1000), #  8
                call(0b0111), #  7
                call(0b0110), #  6
                call(0b0101), #  5
                call(0b0100), #  4
                call(0b0011), #  3
                call(0b0010), #  2
                call(0b0001), #  1
                call(0b0000)  #  0
        ]

        results = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, )

        assert self.bus.scan(minserial, maxserial) == results
        assert self.bus.probe_range.call_args_list == range_list
        assert self.bus.probe_module_short.call_args_list == modules_list

    def test_scan_bus_ButNothingFound(self):
        minserial = 0b0001 #  1
        maxserial = 0b1010 # 10

        self.bus.probe_range = MagicMock()
        self.bus.probe_range.return_value = False

        assert self.bus.scan(minserial, maxserial) is tuple()
        self.bus.probe_range.assert_called_once_with(0b1000)

    @pytest.mark.parametrize("probe", range(33000, 34001))
    def test_scan_AndFindOne(self, probe):
        minserial = 33000
        maxserial = 34000

        def check_range(bcast):
            serno = probe
            while not bcast & 1:
                bcast = bcast >> 1
                serno = serno >> 1
            return (bcast >> 1) == (serno >> 1)

        def check_serno(serno):
            return serno == probe

        self.bus.probe_range = MagicMock()
        self.bus.probe_range.side_effect = check_range

        self.bus.probe_module_short = MagicMock()
        self.bus.probe_module_short.side_effect = check_serno

        assert self.bus.scan(minserial, maxserial) == (probe,)

    def test_find_single_module(self):
        serno      = 31002
        package    = a2b('fd0800ffffff60')
        bytes_recv = a2b('000805ffffffd91a79000042')

        expected_calls = [
            call.cmd.get_negative_ack(),
            call.dev.write_pkg(package),
            call.dev.read_pkg(),
            call.res.get_negative_ack(bytes_recv)
        ]

        self.cmd.get_negative_ack.return_value = package
        self.dev.read_pkg.return_value = bytes_recv
        self.res.get_negative_ack.return_value = serno

        assert self.bus.find_single_module() == serno
        assert self.manager.mock_calls == expected_calls

    def test_find_single_module_FindNothing(self):
        package    = a2b('fd0800ffffff60')
        bytes_recv = DeviceError('Timeout reading header!')

        expected_calls = [
            call.cmd.get_negative_ack(),
            call.dev.write_pkg(package),
            call.dev.read_pkg()
        ]

        self.cmd.get_negative_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.side_effect = bytes_recv

        assert not self.bus.find_single_module()
        assert self.manager.mock_calls == expected_calls

    def test_probe_module_long(self):
        serno      = 31002
        package    = a2b('fd02001a79009f')
        bytes_recv = a2b('0002001a7900a7')

        expected_calls = [
            call.cmd.get_long_ack(serno),
            call.dev.write_pkg(package),
            call.dev.read_pkg(),
            call.res.get_long_ack(bytes_recv, serno)
        ]

        self.cmd.get_long_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.return_value = bytes_recv
        self.res.get_long_ack.return_value = True

        assert self.bus.probe_module_long(serno)
        assert self.manager.mock_calls == expected_calls

    def test_probe_module_long_ButGetDeviceError(self):
        serno      = 31002
        package    = a2b('fd02001a79009f')
        bytes_recv = DeviceError('Timeout reading header!')

        expected_calls = [
            call.cmd.get_long_ack(serno),
            call.dev.write_pkg(package),
            call.dev.read_pkg(),
        ]

        self.cmd.get_long_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.side_effect = bytes_recv

        assert not self.bus.probe_module_long(serno)
        assert self.manager.mock_calls == expected_calls

    def test_probe_module_short(self):
        serno      = 31002
        package    = a2b('fd04001a790003')
        bytes_recv = a2b('24')

        expected_calls = [
            call.cmd.get_short_ack(serno),
            call.dev.write_pkg(package),
            call.dev.read_bytes(1),
            call.res.get_short_ack(bytes_recv, serno)
        ]

        self.cmd.get_short_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_bytes.return_value = bytes_recv
        self.res.get_short_ack.return_value = True

        assert self.bus.probe_module_short(serno)
        assert self.manager.mock_calls == expected_calls

    def test_probe_module_short_ButGetDeviceError(self):
        serno      = 31002
        package    = a2b('fd04001a790003')
        bytes_recv = DeviceError('Timeout reading header!')

        expected_calls = [
            call.cmd.get_short_ack(serno),
            call.dev.write_pkg(package),
            call.dev.read_bytes(1)
        ]

        self.cmd.get_short_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_bytes.side_effect = bytes_recv

        assert not self.bus.probe_module_short(serno)
        assert self.manager.mock_calls == expected_calls

    def test_probe_range(self):
        broadcast  = 0b111100000000000000000000
        package    = a2b('fd06000000f0d0')
        bytes_recv = a2b('ff')

        expected_calls = [
            call.cmd.get_range_ack(broadcast),
            call.dev.write_pkg(package),
            call.dev.read(),
            call.res.get_range_ack(bytes_recv)
        ]

        self.cmd.get_range_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read.return_value = bytes_recv
        self.res.get_range_ack.return_value = True

        assert self.bus.probe_range(broadcast)
        assert self.manager.mock_calls == expected_calls

    def test_probe_range_AndFindNothing(self):
        broadcast  = 0b111100000000000000000000
        package    = a2b('fd06000000f0d0')
        bytes_recv = str()

        expected_calls = [
            call.cmd.get_range_ack(broadcast),
            call.dev.write_pkg(package),
            call.dev.read(),
            call.res.get_range_ack(bytes_recv)
        ]

        self.cmd.get_range_ack.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read.return_value = bytes_recv
        self.res.get_range_ack.return_value = False

        assert not self.bus.probe_range(broadcast)
        assert self.manager.mock_calls == expected_calls

    def test_get(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'
        param = 'SerialNum'
        value = 31002

        tbl = self.ptf.get(table, param)
        pkg = a2b('fd0a031a7900290100c4')
        rcv = a2b('000a051a7900181a79000042')
        val = (value,)

        expected_calls = [
            call.tbl.get(table, param),
            call.cmd.get_parameter(serno, tbl),
            call.dev.write_pkg(pkg),
            call.dev.read_pkg(),
            call.res.get_parameter(serno, tbl, rcv)
        ]

        self.tbl.get.return_value           = tbl
        self.cmd.get_parameter.return_value = pkg
        self.dev.write_pkg.return_value     = True
        self.dev.read_pkg.return_value      = rcv
        self.res.get_parameter.return_value = val

        assert self.bus.get(serno, table, param) == value
        assert self.manager.mock_calls == expected_calls

    def test_get_table(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'
        value = {u"SerialNum":  31002,
                 u"HWVersion":   1.12,
                 u"FWVersion":   1.14,
                 u"Baudrate":    96,
                 u"ModuleName":  "Trime",
                 u"ModuleCode":  100,
                 u"ModuleInfo1": 0,
                 u"ModuleInfo2": 1}

        tbl = self.ptf.get(table)
        pkg = a2b('fd0a031a790029ff0081')
        rcv = a2b('000a231a790061' + '1a790000295c8f3f85eb913f6' +
                  '0005472696d6500000000000000000000006400000171')
        val = [value[param.name] for param in tbl]

        expected_calls = [
            call.tbl.get(table),
            call.cmd.get_table(serno, tbl),
            call.dev.write_pkg(pkg),
            call.dev.read_pkg(),
            call.res.get_table(serno, tbl, rcv)
        ]

        self.tbl.get.return_value       = tbl
        self.cmd.get_table.return_value = pkg
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.return_value  = rcv
        self.res.get_table.return_value = val

        assert self.bus.get_table(serno, table) == value
        assert self.manager.mock_calls == expected_calls

    def test_set(self):
        serno = 31002
        table = 'PROBE_CONFIGURATION_PARAMETER'
        param = 'DeviceSerialNum'
        value = {param: 31003}

        tbl = self.ptf.get(table, param)
        pkg = a2b('fd11071a79002b0c001b790000b0')
        rcv = a2b('0011001a790095')

        expected_calls = [
            call.tbl.get(table, param),
            call.cmd.set_parameter(serno, tbl, param, value, 0),
            call.dev.write_pkg(pkg),
            call.dev.read_pkg(),
            call.res.set_parameter(serno, tbl, rcv)
        ]

        self.tbl.get.return_value = tbl
        self.cmd.set_parameter.return_value = pkg
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.return_value = rcv
        self.res.set_parameter.return_value = True

        assert self.bus.set(serno, table, param, value)
        assert self.manager.mock_calls == expected_calls

    def test_set_table(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'
        vdict = {"SerialNum":  31002,
                 "HWVersion":   1.12,
                 "FWVersion":   1.14,
                 "Baudrate":    96,
                 "ModuleName":  "Trime",
                 "ModuleCode":  100,
                 "ModuleInfo1": 0,
                 "ModuleInfo2": 1}

        tbl = self.ptf.get(table)
        pkg = a2b('fd0b251a79009d' + 'ff00' + '1a790000295c8f3f85eb9' +
                  '13f60005472696d6500000000000000000000006400000181' )
        rcv = a2b('000b001a790054')

        expected_calls = [
            call.tbl.get(table),
            call.cmd.set_table(serno, tbl, vdict),
            call.dev.write_pkg(pkg),
            call.dev.read_pkg(),
            call.res.set_table(serno, tbl, rcv)
        ]

        self.tbl.get.return_value = tbl
        self.cmd.set_table.return_value = pkg
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.return_value = rcv
        self.res.set_table.return_value = True

        assert self.bus.set_table(serno, table, vdict)
        assert self.manager.mock_calls == expected_calls

    def test_set_table_DictHasMissingParam(self):
        serno = 31002
        table = 'SYSTEM_PARAMETER'
        vdict = {"SerialNum":  31002,
                 "HWVersion":   1.12,
                 "FWVersion":   1.14,
                 "Baudrate":    96,
                 "ModuleName":  "Trime",
                 "ModuleCode":  100,
                 "ModuleInfo1": 0}

        tbl = self.ptf.get(table)
        pkg = a2b('fd0b251a79009d' + 'ff00' + '1a790000295c8f3f85eb9' +
                  '13f60005472696d6500000000000000000000006400000181' )
        rcv = a2b('000b001a790054')

        expected_calls = [
            call.tbl.get(table),
        ]

        self.tbl.get.return_value = tbl

        with pytest.raises(AssertionError) as e:
            self.bus.set_table(serno, table, vdict)

        assert e.value.message == 'ModuleInfo2 not in vdict!'
        assert self.manager.mock_calls == expected_calls

    def test_get_eeprom_page(self):
        serno      = 30001
        page_nr    = 0
        page       = [17, 47, 196, 78, 55, 2, 243, 231, 251, 61]
        package    = a2b('fd3c0331750029ff0081')
        bytes_recv = a2b('003c0b1a790015112fc44e3702f3e7fb3dc5')

        expected_calls = [
            call.cmd.get_epr_page(serno, page_nr),
            call.dev.write_pkg(package),
            call.dev.read_pkg(),
            call.res.get_epr_page(bytes_recv)
        ]

        self.cmd.get_epr_page.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.return_value = bytes_recv
        self.res.get_epr_page.return_value = page

        assert self.bus.get_eeprom_page(serno, page_nr) == page
        assert self.manager.mock_calls == expected_calls

    def test_set_eeprom_page(self):
        serno      = 30001
        page_nr    = 7
        page       = [0, 0, 0, 0, 0, 0, 0, 0, 35, 255, 255, 0]
        package    = a2b('fd3d0f317500f6ff07000000000000000023ffff007b')
        bytes_recv = a2b('003d001a79004c')

        expected_calls = [
            call.cmd.set_epr_page(serno, page_nr, page),
            call.dev.write_pkg(package),
            call.dev.read_pkg(),
            call.res.set_epr_page(bytes_recv)
        ]

        self.cmd.set_epr_page.return_value = package
        self.dev.write_pkg.return_value = True
        self.dev.read_pkg.return_value = bytes_recv
        self.res.set_epr_page.return_value = True

        assert self.bus.set_eeprom_page(serno, page_nr, page)
        assert self.manager.mock_calls == expected_calls
