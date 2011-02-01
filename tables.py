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
from yaml import YAMLObject, load_all

try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class Table(YAMLObject):
    """Spezialized Class for wraping YAML Data structures to python objects"""
    yaml_tag = u'!Table'
    
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs) 
    
    def __repr__(self):
        return "%s(Name=%s)" % (
            self.__class__.__name__, self.get_name())
    
    def get_name(self):
        return self.Table['Name']
    
    def _has_parameter(self, param):
        return self.__dict__.has_key(param)
    
    def _get_parameter(self, param):
        return getattr(self, param)

class TablesException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Tables(object):
    """
    >>> t = Tables()
    >>> t.parameter_writable('SYSTEM_PARAMETER_TABLE','SerialNum')
    True
    >>> t.get_parameter_length('SYSTEM_PARAMETER_TABLE','SerialNum')
    8
    >>> t.get_parameter_type('SYSTEM_PARAMETER_TABLE','SerialNum')
    4
    >>> t.get_parameter_no('SYSTEM_PARAMETER_TABLE','SerialNum')
    1
    >>> t.get_table_get_command('SYSTEM_PARAMETER_TABLE')
    10
    >>> t.get_table_set_command('SYSTEM_PARAMETER_TABLE')
    11
    """
    def __init__(self):
        tbl_file = os.path.abspath(__file__)
        tbl_file = os.path.dirname(tbl_file)
        self._file = os.path.join(tbl_file, 'tables.yaml')
        self._loadTables()
    
    def _loadTables(self):
        with open(self._file) as stream:
            tables = self._yamlProjector(load_all(stream, Loader=Loader))
            for table in tables:
                setattr(self, table, tables[table])
        self.mtime = os.stat(self._file).st_mtime
    
    def _modified(self):
        return os.stat(self._file).st_mtime != self.mtime
    
    def _yamlProjector(self, documents):
        manifest = {}
        for table in documents:
            manifest[table.get_name()] = table
        return manifest
        
    def _has_table(self, table):
        if self._modified(): self._loadTables()
        return self.__dict__.has_key(table)
    
    def _has_parameter(self, table, param):
        if self._modified(): self._loadTables()
        return getattr(self, table)._has_parameter(param)
    
    def _get_parameter(self, table, param):
        if self._modified(): self._loadTables()
        
        if not self._has_table(table):
            raise TablesException("ERROR: Table '%s' not known!" % table)
        
        if not self._has_parameter(table, param):
            raise TablesException("ERROR: Table '%s' has no parameter '%s'!"
                % (table,param))
        
        return getattr(self, table)._get_parameter(param)
    
    def parameter_writable(self, table, param):
        return self._get_parameter(table, param)['Status'] == 'WR'
    
    def get_parameter_length(self, table, param):
        return self._get_parameter(table, param)['Length'] * 2
    
    def get_parameter_type(self, table, param):
        return self._get_parameter(table, param)['Type']
    
    def get_parameter_no(self, table, param):
        return self._get_parameter(table, param)['No']
    
    def get_table_get_command(self, table):
        return self._get_parameter(table, 'Table')['Get']
    
    def get_table_set_command(self, table):
        return self._get_parameter(table, 'Table')['Set']
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
