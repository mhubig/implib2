#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (C) 2011-2012, Markus Hubig <mhubig@imko.de>

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
import re, struct
from cStringIO import StringIO
from .imp_helper import _normalize

class EEPRomError(Exception):
    pass

class EEPRom(object):
    def __init__(self):
        self._filename = None
        self._header = dict()
        self._stuff = list()
        self._data = StringIO()

    def __iter__(self):
        for page in range(0, self.pages):
            yield page, self.get_page(page)

    def _reload(self):
        self._filename = None
        self._header = dict()
        self._stuff = list()
        self._data = StringIO()

    def read(self, filename):
        self._reload()
        self._filename = _normalize(filename)
        regex = re.compile('^; (.*?) = (.*?)$')

        with open(self._filename) as epr:
            data = epr.read()

        for line in data.splitlines():
            if not line.startswith(';'):
                byte = int(line.strip())
                self.set_page(struct.pack('>B', byte))
                continue

            match = regex.match(line)
            if match:
                key, value = match.group(1, 2)
                self._header[key] = value
                continue

            self._stuff.append(line.lstrip('; '))

        return True

    def write(self, filename):
        self._filename = _normalize(filename)
        stuff = '; ' + '\n; '.join(self._stuff)
        header = '; ' + '\n; '.join([ '%s = %s' % (x, self._header[x])
            for x in self._header])
        data = self._data.getvalue()
        with open(self._filename, 'w') as epr:
            if self._stuff:
                epr.write(stuff)
            if self._header:
                epr.write(header)
            epr.write(data)

        return True

    def get_page(self, page):
        self._data.seek(page * 252)
        return self._data.read(252)

    def set_page(self, page):
        self._data.seek(0, 2)
        self._data.write(page)
        return True

    @property
    def pages(self):
        pages = self.length / 252
        if self.length % 252:
            pages += 1
        return pages

    @property
    def length(self):
        self._data.seek(0, 2)
        return self._data.tell()

