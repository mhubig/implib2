---
# The *Bus* class

**The Bus object represents the *IMPBus2* master device.**

    class implib2.Bus(port='/dev/ttyUSB0', rs485=False)

**Parameters:**

* *port:* The serial port to use, defaults to `/dev/ttyUSB0`.
* *rs485:* Set this to `True` in order to use the way more relaxed `rs485` timings, defaults to
  `False`.

It is used to initialize and configure the Bus (set the baudrate, find the probes) and provides the
general `get()` and and `set()` methodes. A simple example of how to initialize and search the bus
would be:

    >>> from implib2 import Bus, Module
    >>> bus = Bus('/dev/ttyUSB0')
    >>> bus.sync()
    >>> bus.scan()

## Methode `wakeup()`:

**This command sends a wakeup broadcast command.**

    def wakeup(self):

This command sends a broadcast packet which sets the `EnterSleep` parameter of the
`ACTION_PARAMETER_TABLE` to `0`, which actually means to disable the sleep mode of all connected
modules. But the real aim of this command is to wake up sleeping modules by sending 'something'.

    >>> from implib2 import Bus
    >>> bus = Bus('/dev/ttyUSB0')
    >>> bus.wakeup()
    True

## Methode `sync()`:

**This command synchronises the connected modules to the given baudrate.**

    def sync(self, baudrate=9600):

**Parameters:**

* *baudrate:* The baudrate to set, defaults to `9600`.

The communication between master and slaves can only be successful if they use the same baudrate.
In order to synchronise the modules on a given baudrate, the bus master has to transmit the
broadcast command `SetSysPara` with the parameter Baudrate on all possible baudrates. There must be
a delay of at least `500ms` after each command!

    >>> from implib2 import Bus
    >>> bus = Bus('/dev/ttyUSB0')
    >>> bus.sync()
    True

## Methode `scan()`:

**Command to scan the IMPBUS for connected probes.**

    def scan(self, minserial=0, maxserial=16777215):

**Parameters:**

* *minserial:* Start of the range to search (usually: 0).
* *maxserial:* End of the range to search (usually: 16777215).

This command can be uses to search the IMPBus2 for connected probes. It uses the `probe_range`
command, to address a whole serial number range and in the case of some 'answers' from the range
it recursively devides the range into equal parts and repeads this binary search schema until the
all probes are found.

> **Searching the IMPBus2**

> The 3 bytes IMPBus2 serial numbers spans a 24bit [0 - 16777215] address range, which is a whole
> lot of serial numbers to try. So in order to quickly identify the connected probes the command
> `probe_range` can be used. In order to address more than one probe a a time the header package of
> the :func:`probe_range` command contains a range pattern where you would normaly find the target
> probes serial number. Example: ::
>
>     range serno:   10010001 10000000 00000000 (0x918000)
>     range address: 10010001 00000000 00000000
>     range mark:    00000000 10000000 00000000
>
> As you can see in the example above, the "range serno" from the header package consists of a
> range address and a range marker. The Range marker is alwayse the most right `1` of the
> `range serno`:
>
>     range min:     10010001 00000000 00000000 (0x910000)
>     range max:     10010001 11111111 11111111 (0x91ffff)
>
> So all probes with serial numbers between min and max would answer to a `probe_range` command
> with the `range serno` `0x918000`. The probes would send the CRC of there serial number as reply
> to this command. But because the probes share the same bus it is higly possible the replyes are
> damaged when red from the serial line. So the onoly thing we will know from a `probe_range`
> command is whether or not there is someone in the addressed range. So the next thing to do, if we
> get something back from the addressed range, is to devide the range into two pices by shifting
> the range mark right:
>
>     range mark:  00000000 01000000 00000000 (new range mark)
>     lower half:  10010001 00000000 00000000 (old mark gets 0)
>     higher half: 10010001 10000000 00000000 (old mark gets 1)
>
> So the new `range sernos` (`range address` + `range mark`) are:
>
>     lower half:  10010001 01000000 00000000 (0x914000)
>     higher half: 10010001 11000000 00000000 (0x91c000)
>
> This way we recursively divide the range until we hit the last ranges, spanning only two serial
> numbers. Than we can query them directly, using the `probe_module_short` command.

    >>> from implib2 import Bus
    >>> bus = Bus('/dev/ttyUSB0')
    >>> bus.scan()
    (10010, 10011)

## Methode `find_single_module()`:

**Command to find a single module on the Bus.**

    def find_single_module(self):

This command can be used to identify a single module connected to the bus. It sends a broadcast
command and returns the serial number of the answering module.

**Caution: using this command with multiple modules will result in corrupted aswering packages!**

    >>> from implib2 import Bus
    >>> bus = Bus('/dev/ttyUSB0')
    >>> bus.find_single_module()
    10010

---

# The *Module* class

---

# The *EEPRom* Class
