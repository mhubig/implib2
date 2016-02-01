#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2013, Markus Hubig <mhubig@imko.de>

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

from .imp_helper import _load_json


class TablesError(Exception):
    pass


# pylint: disable=too-few-public-methods
class Tables(object):

    def __init__(self, filename='imp_tables.json'):
        self._tables = _load_json(filename)

    def lookup(self, table, param):
        try:
            cmd = self._tables[table][param]
            cmd[u'Set'] = self._tables[table]["Table"]["Set"]
            cmd[u'Get'] = self._tables[table]["Table"]["Get"]
        except KeyError as err:
            raise TablesError("Unknown param or table: {}!".format(err.message))

        return cmd
