#!/usr/bin/env python
# encoding: utf-8
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
import os, re, struct
from datetime import datetime

class EEPROMError(Exception):
    pass

class EEPROM(object):
    """ Class to parse a EPT file.
    
    The Parser Class has an build in iterator which allowes
    to iter about the eeprom pages stored in this class:
    
    >>> eeprom = EEPROM('../hexfiles/EEPROM.ept')
    >>> buffer = list()
    >>> for nr, page in eeprom:
    ...     buffer.extend(page)
    >>> len(buffer) == eeprom.length
    True
    >>> eeprom.comment[0]
    "Don't change the structure of the file."
    >>> eeprom.version
    '1.120313'
    >>> eeprom.date
    datetime.datetime(2011, 3, 3, 14, 28, 6)
    >>> eeprom.length
    8192
    >>> eeprom.eeprom[0:5]
    [0, 60, 129, 95, 126]
    """
    def __init__(self, filename):
        self._filename = os.path.abspath(filename)
        self._eptbuffer = list()
        self._cmtbuffer = list()
        self._fwversion = str()
        self._eptlength = int()
        self._eptpath = str()
        self._eptdate = str()
        self._read_ept()
    
    def __iter__(self):
        pages = self._eptlength/250
        if pages*250 < self._eptlength:
            pages += 1
        for page in range(0, pages):
            start = page*250
            stop  = start+250
            yield page, self._eptbuffer[start:stop]
    
    def _read_ept(self):
        refwv = re.compile('^; Firmware Version = (.*)$')
        relen = re.compile('^; EPRImage Length = (.*)$')
        repath = re.compile('^; (.:\\\.*)$')
        redate = re.compile('^; (\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d).*?$')
        with open(self._filename) as ept:
            for line in ept.readlines():
                if not line.startswith(';'):
                    self._eptbuffer.append(int(line.strip()))
                if line.startswith(';'):
                    version = refwv.match(line)
                    length  = relen.match(line)
                    path    = repath.match(line)
                    date    = redate.match(line)
                    if version:
                        self._fwversion = float(version.groups()[0].strip())
                    elif length:
                        self._eptlength = int(length.groups()[0])
                    elif path:
                        self._eptpath = os.path.normpath(path.groups()[0].strip())
                    elif date:
                        self._eptdate = datetime.strptime(date.groups()[0], "%Y-%m-%d %H:%M:%S")
                    else:
                        line = line.rstrip()
                        line = line.lstrip('; ')
                        self._cmtbuffer.append(line.strip())
        if not self._eptlength == len(self._eptbuffer):
            raise EPTParserException("ERROR: 'EPRImage Length' dosn't match real length!")
        
        return True
        
    @property
    def eeprom(self):
        return self._eptbuffer
        
    @property
    def comment(self):
        return self._cmtbuffer
        
    @property
    def length(self):
        return self._eptlength
        
    @property
    def version(self):
        return "{0:f}".format(self._fwversion)
        
    @property
    def date(self):
        return self._eptdate
        
    @property
    def file(self):
        return self._filename
        
    @property
    def origin(self):
        return self._eptpath
            
if __name__ == '__main__':
    import doctest
    doctest.testmod()