#!/usr/bin/env python
# encoding: utf-8
import os
from yaml import YAMLObject, load_all

try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Row(type):
    """ Metaclass based Class factory for the table rows. 
    
    This metaclass is used to create Row() classes used
    to build a nested Table() class based on YAML Data. 
    """
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
    
    def __repr__(self):
        return "%s(Name=%s)" % (
            self.__class__.__name__, self.Table.Name)

class TablesException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

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
    >>> t.ACTION_PARAMETER_TABLE.ConfigID.check_writeable()
    False
    """
    def __init__(self, filename='tables.yaml'):
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
