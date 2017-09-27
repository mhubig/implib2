IMPLib2 - Python implementation of the IMPBUS-2 data transmission protocol.
===========================================================================

Travis-CI & Test Coverage
-------------------------

**Stable Branch (0.13.2)**

|Build Status Master| |Test Coverage Master| |Dependecy CI Master|

**Development Branch**

|Build Status Develop| |Test Coverage Develop| |Dependecy CI Develop|

Requirements
------------

Before you can start using the IMPLib2 software you have to make sure,
that you have at least the following software packages installed.

-  Python 2.7 (http://python.org)
-  PySerial (http://pyserial.sourceforge.net)

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
    Python 2.7.3 (default, Aug  1 2012, 05:14:39)
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Import the IMPLib2 module::

    >>> import implib2 as imp

Now initialize the IMPBus, sync and scan for connected Modules. Replace
the USB Interface with the one your SM-USB uses::

    >>> bus = imp.Bus('/dev/ttyUSB0')
    >>> bus.sync()
    >>> bus.scan()
    (10010, 10011)

As you can see we found two connected modules with the serial numbers
10010 and 10011. Now we can instantiate the module objects::

    >>> mod10 = imp.Module(bus, 10010)
    >>> mod11 = imp.Module(bus, 10011)

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
`Read the Docs <https://implib2.readthedocs.org>`__.

.. include:: LICENSE.txt
   :literal:

.. |Build Status Master|
    image:: https://travis-ci.org/mhubig/implib2.svg?branch=master
    :target: https://travis-ci.org/mhubig/implib2
.. |Test Coverage Master|
    image:: https://codecov.io/gh/mhubig/implib2/coverage.svg?branch=master
    :target: https://codecov.io/gh/mhubig/implib2/branch/master
.. |Dependecy CI Master|
    image:: https://dependencyci.com/github/mhubig/implib2/badge
    :target: https://dependencyci.com/github/mhubig/implib2
.. |Build Status Develop|
    image:: https://travis-ci.org/mhubig/implib2.svg?branch=develop
    :target: https://travis-ci.org/mhubig/implib2
.. |Test Coverage Develop|
    image:: https://codecov.io/gh/mhubig/implib2/coverage.svg?branch=develop
    :target: https://codecov.io/gh/mhubig/implib2/branch/develop
.. |Dependecy CI Develop|
    image:: https://dependencyci.com/github/mhubig/implib2/badge
    :target: https://dependencyci.com/github/mhubig/implib2
