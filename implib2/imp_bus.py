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
    """The Bus object represents the IMPBus2 master device. It is used to
    initialize the Bus, set the baudrate and find the connected probes. A
    simple example of how to initialize and search the bus would be::

        >>> from implib2 import Bus, Module
        >>> bus = Bus('/dev/ttyUSB0')
        >>> bus.sync()
        >>> bus.scan()

    :param port: The serial port to use, defaults to `/dev/ttyUSB0`
    :type  port: string

    :param rs485: Set this to `True` in order to use the way more
                  relaxed rs485 timings. Defaults to `False`.
    :type  rs485: bool

    """
    def __init__(self, port='/dev/ttyUSB0', rs485=False):
        tbl = Tables()
        pkg = Package()
        dts = DataTypes()

        self.cmd = Command(tbl, pkg, dts)
        self.res = Responce(tbl, pkg, dts)
        self.dev = Device(port)
        self.dev.open_device()
        self.bus_synced = False

        # timing magic, adds some extra love for rs485
        self.trans_wait = 0.002 if not rs485 else 0.070
        self.cycle_wait = 0.001 if not rs485 else 0.070
        self.range_wait = 0.020 if not rs485 else 0.070

    def _wait(self, package_len, process_time=0.1):
        transit_time = package_len * self.trans_wait
        time.sleep(transit_time + process_time + transit_time)

    def _search(self, range_address, range_marker, found):
        probes = len(found)
        bcast_address = range_address + range_marker

        if not self.probe_range(bcast_address):
            return False

        if range_marker == 1:
            if self.probe_module_short(bcast_address):
                found.append(bcast_address)

            if self.probe_module_short(bcast_address - 1):
                found.append(bcast_address - 1)

            return not probes == len(found)

        # divide-and-conquer by splitting the range into two pices.
        self._search(bcast_address, range_marker >> 1, found)
        self._search(range_address, range_marker >> 1, found)
        return True

    def wakeup(self):
        """This function sends a broadcast packet which sets the 'EnterSleep'
        parameter of the 'ACTION_PARAMETER_TABLE' to '0', which actually means
        to disable the sleep mode of all connected modules. But the real aim of
        this command is to wake up sleeping modules by sending 'something'.

        :rtype: :const:`True`

        """
        address = 16777215  # 0xFFFFFF
        table = 'ACTION_PARAMETER_TABLE'
        param = 'EnterSleep'
        value = 0
        ad_param = 0

        package = self.cmd.set_parameter(address, table, param,
                                         [value], ad_param)

        self.dev.write_pkg(package)
        time.sleep(0.300)

        return True

    def sync(self, baudrate=9600):
        """This command synchronises the connected modules to the given
        baudrate.

        The communication between master and slaves can only be successful
        if they use the same baudrate. In order to synchronise the modules
        on a given baudrate, the bus master has to transmit the broadcast
        command "SetSysPara" with the parameter Baudrate on all possible
        baudrates. There must be a delay of at least 500ms after each command!

        :param baudrate: Baudrate to use (1200-2400-4800-9600).
        :type  baudrate: int

        :raises BusError: If baudrate is unknown.

        :rtype: :const:`True`

        """
        address = 16777215
        table = 'SYSTEM_PARAMETER_TABLE'
        param = 'Baudrate'
        value = baudrate/100
        ad_param = 0

        if value not in (12, 24, 48, 96):
            raise BusError("Unknown baudrate!")

        package = self.cmd.set_parameter(address, table, param,
                                         [value], ad_param)

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

    def scan(self, minserial=0, maxserial=16777215):
        """ Command to scan the IMPBUS for connected probes.

        This command can be uses to search the IMPBus2 for connected probes. It
        uses the :func:`probe_range` command, to address a whole serial number
        range and in the case of some 'answers' from the range it recursively
        devides the range into equal parts and repeads this binary search
        schema until the all probes are found.

        .. note:: Searching the IMPBus2

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
        :type  minserial: int

        :param maxserial: End of the range to search (usually: 16777215).
        :type  maxserial: int

        :rtype: tuple

        """
        sernos = list()
        rng, mark = _imprange(minserial, maxserial)
        self._search(rng, mark, sernos)

        sernos = [x for x in sernos if x >= minserial and x <= maxserial]
        sernos.sort()

        return tuple(sernos)

    def find_single_module(self):
        """ Find a single module on the Bus.

        This command is used to identify a single module on the bus
        which serial number is unknown. It is a broadcast command and
        serves to get the serial number of the module.

        :rtype: :const:`False` or :const:`tuple` containing the serial number.

        """
        package = self.cmd.get_negative_ack()

        try:
            self.dev.write_pkg(package)
            self._wait(len(package))
            bytes_recv = self.dev.read_pkg()
        except DeviceError:
            return False
        finally:
            time.sleep(self.cycle_wait)

        return self.res.get_negative_ack(bytes_recv)

    def probe_module_long(self, serno):
        """ This command with will call up the slave which is addressed
        by its serial number. In return, the slave replies with a
        complete address block. It can be used to test the presence
        of a module in conjunction with the quality of the bus connection.

        :param serno: Serial number of the probe do connect.
        :type  serno: int

        :rtype: :const:`bool`

        """
        package = self.cmd.get_long_ack(serno)

        try:
            self.dev.write_pkg(package)
            self._wait(len(package))
            bytes_recv = self.dev.read_pkg()
        except DeviceError:
            return False
        finally:
            time.sleep(self.cycle_wait)

        return self.res.get_long_ack(bytes_recv, serno)

    def probe_module_short(self, serno):
        """This command will call up the slave which is addressed by its serial
        number. In return, the slave replies by just one byte: The CRC of its
        serial number. It is the shortest possible command without the transfer
        of any data block and the only one without a complete address block. It
        can be used to test the presence of a module.

        :param serno: Serial number of the probe do connect.
        :type  serno: int

        :rtype: :const:`bool`

        """
        package = self.cmd.get_short_ack(serno)

        try:
            self.dev.write_pkg(package)
            self._wait(len(package))
            bytes_recv = self.dev.read_bytes(1)
        except DeviceError:
            return False
        finally:
            time.sleep(self.cycle_wait)

        return self.res.get_short_ack(bytes_recv, serno)

    def probe_range(self, broadcast):
        """ This command is very similar to probe_module_short(). However,
        it addresses not just one single serial number, but a serial
        number range. This is done by setting the values of byte 4 to byte 6
        of the package header to a broadcast pattern. For more details refer to
        the explanation at :func:`scan`.

        :param serno: Broadcast address.
        :type  serno: int

        :rtype: :const:`bool`

        """
        package = self.cmd.get_range_ack(broadcast)
        self.dev.write_pkg(package)
        self._wait(len(package))
        bytes_recv = self.dev.read()
        time.sleep(self.cycle_wait)
        return self.res.get_range_ack(bytes_recv)

    def get(self, serno, table, param):
        """This is the base command for getting some information from the
        probes. Instead of using this command directly, it's highly recommendet
        to use the higher level `API` commands in :class:`Module`. Nevertheless
        here is a small example of how to use this command to request the
        serial number of a probe::

            >>> table = 'SYSTEM_PARAMETER_TABLE'
            >>> param = 'SerialNum'
            >>> serno = 33912
            >>> bus.get(serno, table, param)

        :param serno: Serial number of the probe to request.
        :type  serno: int

        :param table: System table containing the requested infomation.
        :type  table: string

        :param param: Parameter od row containing the requested infomation.
        :type  param: string

        :rtype: :const:`bool`

        """
        package = self.cmd.get_parameter(serno, table, param)
        self.dev.write_pkg(package)
        self._wait(len(package))
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.get_parameter(bytes_recv, table, param)

    def set(self, serno, table, param, value, ad_param=0):
        """This is the base command for sending and storing some information in
        the tables of the probes. It's the counterpart of the :func:`get`
        command. Instead of using this command directly, it's highly
        recommendet to use the higher level `API` commands in :class:`Module`.
        Nevertheless here is a small example of how to use this command to
        set the serial number of a probe::

            >>> table = 'SYSTEM_PARAMETER_TABLE'
            >>> param = 'SerialNum'
            >>> serno = 33912
            >>> new_serno = 33913
            >>> bus.set(serno, table, param, [new_serno])

        :param serno: Serial number of the probe to address.
        :type  serno: int

        :param table: System table to store the infomation.
        :type  table: string

        :param param: Parameter od row containing the requested infomation.
        :type  param: string

        :param value: Values to store.
        :type  value: iterable

        :rtype: :const:`bool`

        """
        # pylint: disable=too-many-arguments
        package = self.cmd.set_parameter(serno, table, param,
                                         value, ad_param)
        self.dev.write_pkg(package)
        self._wait(len(package))
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.set_parameter(bytes_recv, table, serno)

    def get_eeprom_page(self, serno, page_nr):
        """This is the base command for reading a single page of EEPRom data
        from a particular probe. It is later used within some higher `API`
        commands within the :class:`Module`-Class. For more Information please
        refer to the description in the :class:`EEPRom`-Class.

        :param serno: Serial number of the probe to address.
        :type  serno: int

        :param page_nr: EEPRom Page to get.
        :type  page_nr: int

        """
        package = self.cmd.get_epr_page(serno, page_nr)
        self.dev.write_pkg(package)
        self._wait(len(package))
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)
        return self.res.get_epr_page(bytes_recv)

    def set_eeprom_page(self, serno, page_nr, page):
        """This is the base command for writing a single page of EEPRom data
        into a particular probe. It is later used within some higher `API`
        commands within the :class:`Module`-Class. For more Information please
        refer to the description in the :class:`EEPRom`-Class.

        :param serno: Serial number of the probe to address.
        :type  serno: int

        :param page_nr: EEPRom Page to write.
        :type  page_nr: int

        :param page: EEPRom page data.
        :type  page: bytes

        """
        package = self.cmd.set_epr_page(serno, page_nr, page)

        self.dev.write_pkg(package)
        self._wait(len(package))
        bytes_recv = self.dev.read_pkg()
        time.sleep(self.cycle_wait)

        return self.res.set_epr_page(bytes_recv)
