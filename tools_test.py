#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011, Markus Hubig <mhubig@imko.de>

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
from imp_bus import IMPBus, IMPBusError
from imp_modules import Module, ModuleError

bus = IMPBus(port='/dev/tty.usbserial-A700eQFp')
bus.synchronise_bus()
modules = bus.scan_bus()
serno = bus.find_single_module()
print serno
print bus.probe_module_long(serno)
print bus.probe_module_short(serno)

module = modules[0]
print module.get_serial()
print module.get_hw_version()
print module.get_fw_version()
print module.get_moist_min_value()
print module.get_moist_max_value()
print module.get_temp_max_value()
print module.get_temp_min_value()
print module.get_event_mode()
#print module.set_analog_moist(mvolt=500)
#print module.set_analog_temp(mvolt=1000)
#print module.read_eeprom()[0:10]

#module.write_eeprom('../hexfiles/EEPROM.ept')
#module.set_serial(32344)

