#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from struct import pack


class MaximCRC(object):
    def __init__(self):
        self.table = make_table()

    def calc_crc(self, byte_str):
        reg = 0x0
        for char in byte_str:
            idx = (reg ^ ord(char)) & 0xff
            reg = ((reg >> 8) ^ self.table[idx]) & 255
        return pack('>B', reg)

    def check_crc(self, byte_str):
        data = byte_str[:-1]
        crc = byte_str[-1:]
        if not crc == self.calc_crc(data):
            return False
        return True


def reflect(data, width):
    """ Ceflect a data word, means revert the bit order. """
    reflected = data & 0x01
    for _ in range(width - 1):
        data >>= 1
        reflected = (reflected << 1) | (data & 0x01)
    return reflected


def make_table():
    """ Create a traslation table for the MaximCRC algorithm"""
    table = {}
    for i in range(1 << 8):
        register = reflect(i, 8)
        for _ in range(8):
            if register & 128 != 0:
                register = (register << 1) ^ 0x31
            else:
                register = (register << 1)
        register = reflect(register, 8)
        table[i] = register & 255
    return table
