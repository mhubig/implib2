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

.. include:: ../README.rst
   :start-after: ### INCLUDE_FROM_HERE ###


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
