IMPLib2: Python implementation of the IMPBUS-2 protocol.
========================================================

.. image:: https://img.shields.io/pypi/v/implib2.svg
    :target: https://pypi.python.org/pypi/implib2

.. image:: https://img.shields.io/pypi/pyversions/implib2.svg
    :target: https://pypi.python.org/pypi/implib2

.. image:: https://img.shields.io/pypi/l/implib2.svg
    :target: https://pypi.python.org/pypi/implib2

.. image:: https://travis-ci.org/mhubig/implib2.svg?branch=master
    :target: https://travis-ci.org/mhubig/implib2

.. image:: https://codecov.io/gh/mhubig/implib2/coverage.svg?branch=master
    :target: https://codecov.io/gh/mhubig/implib2/branch/master

---------------

Requirements
------------

Before you can start using the IMPLib2 software you have to make sure,
that you have at least the following software packages installed.

- Python (http://python.org)
- PySerial (http://pyserial.sourceforge.net)

For instructions on how to get and install these packages on your OS
please head over to the official project pages.

Installation
------------

Install the stable branch using pip::

    pip install implib2

Of if you brave enough::

    pip install git+https://github.com/mhubig/implib2.git@develop

Depending on your system you may have to prefix these commands with ``sudo``!

Quick Start Manual
------------------

This small quick start manual is intended to give you a basic example of
how to use this library. In order to start playing with it you have to
connect at least one `Trime
Pico <http://imko.de/en/products/soilmoisture>`__ moisture measurement
probe to your computer. An easy way to connect the probe is by using the
USB-IMPBus Converter `SM-USB <http://imko.de/en/products>`__.

After successfully installing IMPLib2 and connecting, start the Python
Shell within your terminal::

    $ python
    Python 3.6.2 (default, Jul 17 2017, 16:44:45)
    [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Import the IMPLib2 module::

    >>> import implib2

Now initialize the IMPBus, sync and scan for connected Modules. Replace
the USB Interface with the one your SM-USB uses::

    >>> bus = implib2.Bus('/dev/ttyUSB0')
    >>> bus.sync()
    >>> bus.scan()
    (10010, 10011)

As you can see we found two connected modules with the serial numbers
10010 and 10011. Now we can instantiate the module objects::

    >>> mod10 = implib2.Module(bus, 10010)
    >>> mod11 = implib2.Module(bus, 10011)

Using the handy module objects we can now perform various higher
operations, like doing a measurement or requesting the serial number::

    >>> mod10.get_moisture()
    14.3
    >>> mod11.get_moisture()
    17.4
    >>> mod10.get_serno()
    10010

    10011

If you came so far you should be able to easily build a little script
which performs an measurement on all connected probes ones an hour::

    #!/usr/bin/env python

    import time
    import implib2

    # Initialize the IMPBus2
    bus = implib2.Bus('/dev/ttyUSB0')
    bus.sync()

    # Search the bus for connected modules
    modules = [implib2.Module(bus, serno) for serno in bus.scan()]

    # Start a measurement and show the results once an hour
    while True:
        for module in modules:
            serno = module.get_serno()
            moist = module.get_moisture()
            temp = module.get_measure(quantity='MeasTemp')
            print('Module {}: Moist {}, Temp {}'.format(serno, moist, mtemp))

        time.sleep(3600)  # for one hour

For more and in depth information please head over to the API-Documentation on
`Read the Docs <https://implib2.readthedocs.org>`__.

.. include:: LICENSE.txt
   :literal:
