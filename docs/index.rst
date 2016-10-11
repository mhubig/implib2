IMPBUS-2 Library
================

This library is a python implementation of the "Data transmission protocol for
IMPBus2" called IMPBus2. IMPBus2 is a fieldbus system to which up to 250 single
slaves may be connected by a bi-directional 2-wire line. The modules are
controlled by the bus master, typically this is the host computer. Each
computer with a standard RS-232 interface can be used as the bus master. The
master is able to send a set of commands to the slaves, to start actions or to
acquire data. The IMPBus-2 itself is interfaced by a special active adapter
(SM23U or SM-USB, please contact the `IMKO GmbH`_ for more informations).

The communication is based on the transmission of address- and data blocks. The
transmission itself uses asynchronous symbolic address-based and byte-based
protocols. Up to 250 bytes of significant data can be transmitted
bi-directional in one telegram.

This library is typically used to access `TRIME Pico`_ moisture measurements
probes. It is tested for Python 2.7 running on Linux, Windows and MacOSX.

Requirements
============

Before you can start using the IMPLib2 software you have to make sure, that
you have at least the following software packages installed.

- Python 2.7 (http://python.org)
- PySerial 2.7 (http://pyserial.sourceforge.net)

For instructions on how to get and install these packages on your OS please
head over to the official project pages.


Installation
============

Install the stable branch using pip::

    $ pip install implib2

Of if you brave enough::

    $ pip install git+https://github.com/mhubig/implib2.git@develop

Depending on your system you may have to prefix these commands with ``sudo``!


Quick Start Manual
==================

This small quick start manual is intended to give you a basic example of how
to use this library. In order to start playing with it you have to connect at
least one `Trime Pico`_ moisture measurement probe to your computer. An easy
way to connect the probe is by using the USB-IMPBus Converter SM-USB_.

After successfully installing IMPLib2 and connecting, start the Python Shell
within your terminal::

    $ python
    Python 2.7.3 (default, Aug  1 2012, 05:14:39)
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Import the IMPLib2 module::

    >>> import implib2 as imp

Now initialize the IMPBus, sync and scan for connected Modules. Replace the
USB Interface with the one your SM-USB uses::

    >>> bus = imp.Bus('/dev/ttyUSB0')
    >>> bus.sync()
    >>> bus.scan()
    (10010, 10011)

As you can see we found two connected modules with the serial numbers 10010
and 10011. Now we can instantiate the module objects::

    >>> mod10 = imp.Module(bus, 10010)
    >>> mod11 = imp.Module(bus, 10011)

Using the handy module objects we can now perform various higher operations,
like doing a measurement or requesting the serial number::

    >>> mod10.get_moisture()
    14.3
    >>> mod11.get_moisture()
    17.4
    >>> mod10.get_serno()
    10010
    >>> mod11.get_serno()
    10011

If you came so far you should be able to easily build a little script which
performs an measurement on all connected probes ones an hour::

    #!/usr/bin/env python
    # -*- coding: UTF-8 -*-

    import time
    import implib2 as imp

    # Initialize the IMPBus2
    bus = imp.Bus('/dev/ttyUSB0')
    bus.sync()

    # Search the bus for connected modules
    modules = [imp.Module(bus, serno) for serno in bus.scan()]

    # Start a measurement and show the results once an hour
    while True:
        for module in modules:
            serno = module.get_serno()
            moist = module.get_moisture()
            mtemp = module.get_measure(quantity='MeasTemp')
            print "Module {}: Moist {}, Temp {}".format(serno, moist, mtemp)

        time.sleep(3600)  # for one hour

For more and in depth information please head over to the API-Documentation on
`Read the Docs`_.


License
=======

::

    MIT License

    Copyright (c) 2011-2016 Markus Hubig

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.


.. _Trime Pico: http://imko.de/en/products/soilmoisture
.. _Read the Docs: https://implib2.readthedocs.org
.. _SM-USB: http://imko.de/en/products


The API Documentation
---------------------

.. toctree::
   :maxdepth: 2

   implib2.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _IMKO GmbH: http://imko.de
.. _Trime Pico: http://imko.de/en/products/soilmoisture
