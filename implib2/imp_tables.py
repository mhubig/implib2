#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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
