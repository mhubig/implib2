#!/usr/bin/env python
# -*- coding: UTF-8 -*-


# pylint: disable=too-few-public-methods
class DataTypes(object):

    def __init__(self):
        self._dtypes = {
            0x00: '<{0}B',  # 08-bit unsigned char
            0x01: '<{0}b',  # 08-bit signed char
            0x02: '<{0}H',  # 16-bit unsigned short
            0x03: '<{0}h',  # 16-bit signed short
            0x04: '<{0}I',  # 32-bit unsigned integer
            0x05: '<{0}i',  # 32-bit signed integer
            0x06: '<{0}f',  # 32-bit float
            0x07: '<{0}d'}  # 64-bit double

    def __contains__(self, item):
        return item in self._dtypes

    def lookup(self, dtype):
        return self._dtypes[dtype]
