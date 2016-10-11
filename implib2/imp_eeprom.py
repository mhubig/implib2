#!/usr/bin/env python
# encoding: utf-8

import io
import re
import struct


# pylint: disable=too-few-public-methods
class EEPROM(object):
    """This Class represents a simple data structure to hold an EEPROM
    image. It can be used with :func:`Module.write_eeprom` to update the
    EEPROM image of the probe.
    """

    def __init__(self, filename):
        self._data = io.BytesIO()
        self._page = 250
        self._regx = re.compile('^; (.*?) = (.*?)$')

        with open(filename) as epr:
            for line in epr:
                if line.startswith(';'):
                    self._readmeta(line)
                else:
                    self._readdata(line)

        self._data.seek(0)

    def __iter__(self):
        while True:
            data = self._data.read(self._page)
            if not data:
                break
            yield data

    def _readdata(self, line):
        byte = struct.pack('>B', int(line.strip()))
        self._data.write(byte)

    def _readmeta(self, line):
        match = self._regx.match(line)
        if match:
            key, value = match.group(1, 2)
            setattr(self, key.replace(' ', '_').strip(), value.strip())
