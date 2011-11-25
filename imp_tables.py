#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011, Markus Hubig <mhubig@imko.de>

This file is part of IMPLib2 a small Python library implementing
the IMPBUS-2 data transmission protocol.

IMPLib2 is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

IMPLib2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with IMPLib2. If not, see <http://www.gnu.org/licenses/>.
"""

import os
from yaml import YAMLObject, load_all
from yaml import Loader, Dumper

class Row(type):
    """ Metaclass based Class factory for the table rows. 
    
    This metaclass is used to create Row() classes used
    to build a nested Table() class based on YAML Data. 
    """
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        cls.DEBUG = False
        super(Row, cls).__init__(name, bases, dct)

    def check_length(cls, value):
        if not len(value) == cls.Length*2: return False
        return True

    # TODO: implement a type check
    def check_type(cls, value):
        return True

    def writeable(cls):
        if cls.Status != 'WR': return False
        return True

class Table(YAMLObject):
    """Spezialized Class for building python objects from YAML data.
    
    This class is used by the YAML Loader (see yaml.load_all) to
    convert YAML Data tagged with '!Table' to a nested Python class.
    The class is nested with Row() classes by overwriting __setstate__()
    accourding to the pickle protocol. For more details see:
    http://docs.python.org/library/pickle.html#object.__setstate__
    """
    yaml_tag = u'!Table'

    def __setstate__(self, dct):
        for key, value in dct.items():
            row = Row(key, (object,), value)
            self.__dict__.update({key: row})
    
    def __init__(self):
        self.DEBUG = False
        
    def __repr__(self):
        return "%s(Name=%s)" % (
            self.__class__.__name__, self.Table.Name)

class TablesError(Exception):
    pass

class Tables(object):
    """ Class containing all the IMPBUS2 parameter Tables.

    This Class reads the YAML file containing all the parameter
    tables of the IMPBUS2 secification and builds a nested class
    structur of it. You can use introspection to brows thru the
    Tables.

    >>> t = Tables()
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.No
    251
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.check_length('0000')
    True
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.check_type('0a')
    True
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.writeable()
    False
    """
    def __init__(self, filename='imp_tables.yaml'):
        self.DEBUG = False
        self._file = self._normalize(filename)
        self._add_sub_classes()

    def _normalize(self, filename):
        abs_path = os.path.abspath(__file__)
        dir_name = os.path.dirname(abs_path)
        return os.path.join(dir_name, filename)

    def _add_sub_classes(self):
        with open(self._file) as stream:
            for table in load_all(stream, Loader=Loader):
                self.__dict__.update({table.Table.Name : table})
       
if __name__ == "__main__":
    import doctest
    doctest.testmod()
