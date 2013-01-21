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

from .imp_device import Device, DeviceError
from .imp_datatypes import DataTypes
from .imp_packages import Package
from .imp_commands import Command
from .imp_responces import Responce
from .imp_tables import Tables
from .imp_helper import _imprange

class BusError(Exception):
    pass

class Bus(object):
    def __init__(self, port='/dev/ttyUSB0', rs485=False):
        tbl = Tables()
        pkg = Package()
        dts = DataTypes()

        self.cmd = Command(tbl, pkg, dts)
        self.res = Responce(tbl, pkg, dts)
        self.dev = Device(port)
        self.bus_synced = False

        # timing magic, adds some extra love for rs485
        self.trans_wait = 0.001 if not rs485 else 0.070
        self.cycle_wait = 0.020 if not rs485 else 0.070
        self.range_wait = 0.020 if not rs485 else 0.070

    def _search(self, range_address, range_marker, found):
        """ Recursiv divide-and-conquer algorithm to scan the IMPBUS.

        :param range_address: Address range to search.
        :param range_marker: Range start marker.
        :param found: Container to store the found modules.
        :type found: list
        :rtype: bool

        Divides the given range address by shifting the mark bit left and use
        the get_range_ack() methode to sort out the rages without a module. The
        found module serials are stored in the parameter list 'found'.
        """
        probes = len(found)
        broadcast = range_address + range_marker

        if not self.probe_range(broadcast):
            return False

        if range_marker == 1:
            if self.probe_module_short(broadcast):
                found.append(broadcast)

            if self.probe_module_short(broadcast - 1):
                found.append(broadcast - 1)

            return not probes == len(found)

        # divide-and-conquer by splitting the range into two pices.
        self._search(broadcast,     range_marker >> 1, found)
        self._search(range_address, range_marker >> 1, found)
        return True

    def wakeup(self):
        """ This function sends out a broadcast packet which sets the
        'EnterSleep' parameter of the 'ACTION_PARAMETER_TABLE' to '0', which
        actually means to disable the sleep mode of all connected modules. But
        the real aim of this command is to wake up sleeping modules be sending
        'something'.
        """
        address  = 16777215 # 0xFFFFFF
        table    = 'ACTION_PARAMETER_TABLE'
        param    = 'EnterSleep'
        value    = 0
        ad_param = 0

        package = self.cmd.set_parameter(address, table,
                param, [value], ad_param)

        self.dev.write_pkg(package)
        time.sleep(0.300)

        return True

    def synchronise_bus(self, baudrate=9600):
        """ IMPBus2 baudrate syncroisation.

        :param baudrate: Serial baudrate to use (e.g.: 9600)
        :type baudrate: int

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

        package = self.cmd.set_parameter(address, table,
                param, [value], ad_param)

        # first close the device
        self.dev.close_device()

        # trying to set baudrate at 1200
        self.dev.open_device(baudrate=1200)
        self.dev.write_pkg(package)
        time.sleep(0.500)
        self.dev.close_device()

        # trying to set baudrate at 2400
        self.dev.open_device(baudrate=2400)
        self.dev.write_pkg(package)
        time.sleep(0.420)
        self.dev.close_device()

        # trying to set baudrate at 4800
        self.dev.open_device(baudrate=4800)
        self.dev.write_pkg(package)
        time.sleep(0.340)
        self.dev.close_device()

        # trying to set baudrate at 9600
        self.dev.open_device(baudrate=9600)
        self.dev.write_pkg(package)
        time.sleep(0.260)
        self.dev.close_device()

        # at last open the device with the setted baudrate
        self.dev.open_device(baudrate=baudrate)
        self.bus_synced = True
        time.sleep(1.000)

        return True

    def scan_bus(self, minserial=0, maxserial=16777215):
        """ Command to scan the IMPBUS for connected probes.

        This command can be uses to search the IMPBus2 for connected probes. It
        uses the :func:`probe_range` command, to address a whole serial number
        range and in the case of some 'answers' from the range it recursively
        devides the range into equal parts and repeads this binary search
        schema until the all probes are found.

        .. admonition:: Searching the IMPBus2

            The 3 bytes IMPBus2 serial numbers spans a 24bit [0 - 16777215]
            address range, which is a whole lot of serial numbers to try. So in
            order to quickly identify the connected probes the command
            :func:`probe_range` can be used. In order to address more than one
            probe a a time the header package of the :func:`probe_range`
            command contains a range pattern where you would normaly find the
            target probes serial number. Example: ::

                range serno:   10010001 10000000 00000000 (0x918000)
                range address: 10010001 00000000 00000000
                range mark:    00000000 10000000 00000000

            As you can see in the example above, the "range serno" from the
            header package consists of a range address and a range marker. The
            Range marker is alwayse the most right '1' of the "range serno"::

                range min:     10010001 00000000 00000000 (0x910000)
                range max:     10010001 11111111 11111111 (0x91ffff)

            So all probes with serial numbers between min and max would answer
            to a :func:`probe_range` command with the "range serno" 0x918000.
            The probes would send the CRC of there serial number as reply to
            this command. But because the probes share the same bus it is higly
            possible the replyes are damaged when red from the serial line. So
            the onoly thing we will know from a :func:`probe_range` command is
            whether or not there is someone in the addressed range. So the next
            thing to do, if we get something back from the addressed range, is
            to devide the range into two pices by shifting the range mark
            right::

                range mark:  00000000 01000000 00000000 (new range mark)
                lower half:  10010001 00000000 00000000 (old mark gets 0)
                higher half: 10010001 10000000 00000000 (old mark gets 1)

            So the new "range sernos" ("range address" + "range mark") are::

                lower half:  10010001 01000000 00000000 (0x914000)
                higher half: 10010001 11000000 00000000 (0x91c000)

            This way we recursively divide the range until we hit the last
            ranges, spanning only two serial numbers. Than we can query them
            directly, using the :func:`probe_module_short` command.

        :param minserial: Start of the range to search (usually: 0).
        :type minserial: int
        :param maxserial: End of the range to search (usually: 16777215).
        :type maxserial: int
        :rtype: tuple
        """
        sernos  = list()
        rng, mark = _imprange(minserial, maxserial)
        self._search(rng, mark, sernos)

        sernos = [x for x in sernos if x >= minserial and x <= maxserial]
        sernos.sort()

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
            time.sleep(self.trans_wait)
            bytes_recv = self.dev.read_pkg()
        except DeviceError:
            return False
        finally:
            time.sleep(self.cycle_wait)

        return self.res.get_negative_ack(bytes_recv)

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
            time.sleep(self.trans_wait)
            bytes_recv = self.dev.read_pkg()
        except DeviceError:
            return False
        finally:
            time.sleep(self.cycle_wait)

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
            time.sleep(self.trans_wait)
            bytes_recv = self.dev.read_bytes(1)
        except DeviceError:
            return False
        finally:
            time.sleep(self.cycle_wait)

        return self.res.get_short_ack(bytes_recv, serno)

    def probe_range(self, broadcast):
        """ PROBE ADDRESSRANGE

        This command is very similar to probe_module_short(). However,
        it addresses not just one single serial number, but a serial
        number range. This value of byte 4 to byte 6 symbolizes a
        whole range according to a broadcast pattern. For more details
        refer to the doctring of get_acknowledge_for_serial_number_range()
        or the the "Developers Manual, Data Transmission Protocol for
        IMPBUS2, 2008-11-18".
        """
        package = self.cmd.get_range_ack(broadcast)
        self.dev.write_pkg(package)
        time.sleep(self.range_wait)
        bytes_recv = self.dev.read()
        time.sleep(self.cycle_wait)
        return self.res.get_range_ack(bytes_recv)

    def get(self, serno, table, param):
        package = self.cmd.get_parameter(serno, table, param)
        self.dev.write_pkg(package)
        time.sleep(self.trans_wait)
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.get_parameter(bytes_recv, table, param)

    def set(self, serno, table, param, value, ad_param=0):
        # pylint: disable=R0913
        package = self.cmd.set_parameter(serno, table, param,
                value, ad_param)
        self.dev.write_pkg(package)
        time.sleep(self.trans_wait)
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.set_parameter(bytes_recv, serno, table)

    def get_eeprom_page(self, serno, page_nr):
        package = self.cmd.get_epr_page(serno, page_nr)
        self.dev.write_pkg(package)
        time.sleep(self.trans_wait)
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.get_epr_page(bytes_recv)

    def set_eeprom_page(self, serno, page_nr, page):
        package = self.cmd.set_epr_page(serno, page_nr, page)
        self.dev.write_pkg(package)
        time.sleep(self.trans_wait)
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.set_epr_page(bytes_recv)

