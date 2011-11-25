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

import time

from imp_bus import IMPBus, IMPBusError
from imp_modules import Module, ModuleError
bus = IMPBus(port='/dev/ttyUSB0')
bus.synchronise_bus(baudrate=9600)
module = bus.find_single_module()
print module.get_serial()
print module.get_serial()
print module.get_serial()
print module.get_serial()
print module.get_event_mode()

time.sleep(2.0)

print module.get_moisture()
