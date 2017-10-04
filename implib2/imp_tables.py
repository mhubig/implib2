# -*- coding: UTF-8 -*-

from .imp_helper import _load_json


class TablesError(Exception):
    pass


class Tables:

    def __init__(self, filename='imp_tables.json'):
        self._tables = _load_json(filename)

    def _lookup_param(self, table, param):
        try:
            return table[param]
        except KeyError as err:
            raise TablesError("Unknown param: {}!".format(err))

    def _lookup_table(self, table):
        try:
            return self._tables[table]
        except KeyError as err:
            raise TablesError("Unknown table: {}!".format(err))

    def lookup(self, table, param=None):
        result = self._lookup_table(table)

        if not param:
            return result

        result = self._lookup_param(result, param)
        result['Set'] = self._tables[table]["Table"]["Set"]
        result['Get'] = self._tables[table]["Table"]["Get"]

        return result
