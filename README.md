Requirements
============

Before you can use the IMPLib2 software you have to make sure that
you have at least the following software installed.

- Python 2.7 (http://python.org)
- PySerial 2.5 (http://pyserial.sourceforge.net)

Installation
============

Just install the stable branch with pip using git::

    $ pip install git+http://bitbucket.org/imko/implib2.git@master

Of if you brave enough::

    $ pip install git+http://bitbucket.org/imko/implib2.git@develop

Depending on your system you may have to prefix these commands with ``sudo``!

Travis-CI Build Status & Test Coverage
======================================

[![Build Status](https://travis-ci.org/mhubig/implib2.png?branch=develop)](https://travis-ci.org/mhubig/implib2)
[![Coverage Status](https://coveralls.io/repos/mhubig/implib2/badge.png)](https://coveralls.io/r/mhubig/implib2)

Quick Start Manual
==================

This small quick start manual is intended to give you a basic example of how to
use this library. In order to start playing with it you have to connect at
least one `Trime Pico`_ moisture measurement probe to your computer. An easy
way to connect the probe is by using the USB-IMPBus Converter SM-USB.

If you successfully installed the IMPLib2, start the Python CLI within you
terminal::

    $ python
    Python 2.7.3 (default, Aug  1 2012, 05:14:39) 
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Import the IMPLib2 modules::

    >>> from implib2 import Bus, Module

Now initialize the IMPBus, and sync and scan for connected Modules. Replace
the USB Interface with the one you SM-USB uses::

    >>> bus = Bus('/dev/ttyUSB0')
    >>> bus.sync()
    >>> bus.scan()
    (10010, 10011)

As you can see we have found two connected modules with ser serial numbers
10010 and 10011. Now we can instantiate the modules::

    >>> mod10 = Module(bus, 10010)
    >>> mod11 = Module(bux, 10011)

With the Module objects we can now perform various operations, like doing a
measurement or requesting the serial number::

    >>> mod10.get_moisture()
    14.3
    >>> mod11.get_moisture()
    17.4
    >>> mod10.get_serno()
    10010
    >>> mos11.get_serno()
    10011

With this information we can easily build a little script which performs an
measurement on all connected probes ones an hour::

    #!/usr/bin/env python
    # -*- coding: UTF-8 -*-

    import time
    from implib2 import Bus, Module

    bus = Bus('/dev/ttyUSB0')
    bus.sync()

    modules = []
    for serno in bus.scan():
        modules.append(Module(bus, serno))

    while True:
        for module in modules:
            serno = module.get_serno()
            moist = module.get_moist()
            print serno, moist
        time.sleep(3600) # one hour

License
=======

> Copyright (C) 2011-2013, Markus Hubig <mhubig@imko.de>
>
> This is the documentation part of IMPLib2, a small Python library
> implementing the IMPBUS-2 data transmission protocol.
>
> IMPLib2 is free software: you can redistribute it and/or modify
> it under the terms of the GNU Lesser General Public License as
> published by the Free Software Foundation, either version 3 of
> the License, or (at your option) any later version.
>
> IMPLib2 is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
> GNU Lesser General Public License for more details.
>
> You should have received a copy of the GNU Lesser General Public
> License along with IMPLib2. If not, see <http://www.gnu.org/licenses/>.
