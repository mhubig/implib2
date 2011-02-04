#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2012, Markus Hubig <mhubig@imko.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import os
from yaml import load_all

try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Row(type):
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(Row, cls).__init__(name, bases, dct)

    def check_length(cls, value):
        if not len(value) == cls.Length*2: return False
        return True
    
    # TODO: implement a type check
    def check_type(cls, value):
        return True
        
    def check_writeable(cls):
        if cls.Status != 'WR': return False
        return True
           
class Table(type):
    def __new__(cls, name, bases, dct):
        default_rows = {'ConfigID' : 0xfb, 'TableSize': 0xfc,
                        'Parameter': 0xfd, 'DataSize' : 0xfe,
                        'TableData': 0xff}
        for key, value in default_rows.items():
            entrys = {'No': value, 'Type': 0x02, 'Status': 'OR', 'Length': 2}
            dct.update({key: Row(key, (object,), entrys)})
        return type.__new__(cls, name, bases, dct)
        
    def __init__(cls, name, bases, dct):
        super(Table, cls).__init__(name, bases, dct)

class Tables(object):
    """ Class containing all the IMPBUS2 parameter Tables.
    
    This Class reads the YAML file containing all the parameter
    tables of the IMPBUS2 secification and builds a nested class
    structur of it. You can use introspection to brows thru the
    Tables.
    
    >>> t = Tables('tables.yaml')
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.No
    251
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.check_length('0000')
    True
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.check_type('0a')
    True
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.check_writeable()
    False
    """
    def __init__(self, filename):
        self._subc = dict()
        self._build_sub_classes(filename)
        
        for subc in self._subc: 
            setattr(self, subc, self._subc[subc])

    def _build_sub_classes(self, filename):
        dir_name = os.path.abspath(__file__)
        dir_name = os.path.dirname(dir_name)
        filename = os.path.join(dir_name, filename)
        with open(filename) as stream:
            for table in load_all(stream, Loader=Loader):
                name = table['Table']['Name']
                rows = dict()
                for row in table:
                    rows.update({row : Row(row, (object,), table[row])})
                self._subc.update({name : Table(name, (object,), rows)})

if __name__ == "__main__":
    import doctest
    doctest.testmod()