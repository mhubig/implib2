#!/usr/bin/env python
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
import time

from binascii import b2a_hex as b2a, a2b_hex as a2b

from imp_device import Device, DeviceError
from imp_tables import Tables, TablesError
from imp_packages import Package, PackageError
from imp_commands import Command, CommandError
from imp_responces import Responce, ResponceError

class BusError(Exception):
    pass

class Bus(object):
    def __init__(self, device):
        tables = Tables()
        package = Package()
        self.cmd = Command(tables, package)
        self.res = Responce(tables, package)
        self.dev = device
        self.bus_synced = False

    def _divide_and_conquer(self, low, high, found):
        """ Recursiv divide-and-conquer algorithm to scan the IMPBUS.

        Divides the given address range [max 24bit, 0 - 16777215] in equal
        parts and uses the get_range_ack() methode to sort out the rages
        without a module. The found module serials are stored in the parameter
        list 'found'.
        """

        # if we have only one serial left check them direct.
        if high == low:
            if self.probe_module_short(high):
                found.append(high)
                return True
            return False
        else:
            # calculate the broadcast address for range [low-high] and check
            # if there are some modules whithin the range, abort if not!
            broadcast = low + (high-low+1)/2
            if not self.probe_range(broadcast):
                return False

        # divide-and-conquer by splitting the range into two pices.
        mid = (low + high)/2
        self._divide_and_conquer(low, mid, found)
        self._divide_and_conquer(mid+1, high, found)
        return True

    def synchronise_bus(self, baudrate=9600):
        """ IMPBUS BAUDRATE SYNCHRONIZATION

        The communication between master and slaves can only be successful
        if they are on the same baud rate. In order to synchronise SM-modules
        on a given baud rate, the bus master has to transmit the broadcast
        command "SetSysPara" with the parameter Baudrate on all possible baud
        rates (1200-2400-4800-9600). There must be a delay of at least 500ms
        after each command! The SM-modules understands one of these commands
        and will switch to the desired baud rate.
        """
        address  = 16777215
        table    = 'SYSTEM_PARAMETER_TABLE'
        param    = 'Baudrate'
        value    = baudrate/100
        ad_param = 0

        if not value in (12, 24, 48, 96):
            raise BusError("Unknown baudrate!")

        # first close the device
        self.dev.close_device()

        # trying to set baudrate at 1200
        self.dev.open_device(baudrate=1200)
        package = self.cmd.set_parameter(address, table,
                param, [value], ad_param)
        bytes_send = self.dev.write_pkg(package)
        time.sleep(0.5)
        self.dev.close_device()

        # trying to set baudrate at 2400
        self.dev.open_device(baudrate=2400)
        package = self.cmd.set_parameter(address, table, param,
                [value], ad_param)
        bytes_send = self.dev.write_pkg(package)
        time.sleep(0.5)
        self.dev.close_device()

        # trying to set baudrate at 4800
        self.dev.open_device(baudrate=4800)
        package = self.cmd.set_parameter(address, table, param,
                [value], ad_param)
        bytes_send = self.dev.write_pkg(package)
        time.sleep(0.5)
        self.dev.close_device()

        # trying to set baudrate at 9600
        self.dev.open_device(baudrate=9600)
        package = self.cmd.set_parameter(address, table, param,
                [value], ad_param)
        bytes_send = self.dev.write_pkg(package)
        time.sleep(0.5)
        self.dev.close_device()

        # at last open the device with the setted baudrate
        self.dev.open_device(baudrate=baudrate)
        self.bus_synced = True
        time.sleep(0.5)

        return True

    def scan_bus(self, minserial=0, maxserial=16777215):
        """ High level command to scan the IMPBUS for connected probes.

        This command is very similar to the short_probe_module() one. However,
        it addresses not just one single serial number, but a whole serial
        number range. The values of byte 4 to byte 6 of the IMPBus2 header
        package spans a 24bit [0 - 16777215] address range.

        It's basiclly just a small wrapper around _divide_and_conquer().
        """

        sernos  = list()
        self._divide_and_conquer(minserial, maxserial, sernos)

        return tuple(sernos)

    def find_single_module(self):
        """ Find a single module on the Bus

        This command is used to identify a single module on the bus
        which serial number is unknown. It is a broadcast command and
        serves to get the serial number of the module. This command
        returns a Modules Object.
        """
        package = self.cmd.get_negative_ack()
        try:
            self.dev.write_pkg(package)
            bytes_recv = self.dev.read_pkg()
        except DeviceError as e:
            return (False,)
        serno = self.res.get_negative_ack(bytes_recv)
        return (serno,)

    def probe_module_long(self, serno):
        """ PROBE MODULE (LONGCOMMAND)

        This command with will call up the slave which is addressed
        by its serial number. In return, the slave replies with a
        complete address block. It can be used to test the presence
        of a module in conjunction with the quality of the bus connection.
        """
        package = self.cmd.get_long_ack(serno)
        try:
            self.dev.write_pkg(package)
            bytes_recv = self.dev.read_pkg()
        except DeviceError as e:
            return False
        return self.res.get_long_ack(bytes_recv, serno)

    def probe_module_short(self, serno):
        """ PROBE MODULE (SHORTCOMMAND)

        This command will call up the slave which is addressed
        by its serial number. In return, the slave replies by
        just one byte: The CRC of its serial number. It is the
        shortest possible command without the transfer of any
        data block and the only one without a complete address
        block. It can be used to test the presence of a module.
        """
        package = self.cmd.get_short_ack(serno)
        try:
            self.dev.write_pkg(package)
            bytes_recv = self.dev.read_bytes(1)
        except DeviceError as e:
            return False
        return self.res.get_short_ack(bytes_recv, serno)

    def probe_range(self, broadcast):
        """ PROBE ADDRESSRANGE

        This command is very similar to the previous one. However,
        it addresses not just one single serial number, but a serial
        number range. This value of byte 4 to byte 6 symbolizes a
        whole range according to a broacast pattern. For more details
        refer to the doctring of get_acknowledge_for_serial_number_range()
        or the the "Developers Manual, Data Transmission Protocol for
        IMPBUS2, 2008-11-18".
        """
        package = self.cmd.get_range_ack(broadcast)
        self.dev.write_pkg(package)
        bytes_recv = self.dev.read_something()
        return self.res.get_range_ack(bytes_recv)

