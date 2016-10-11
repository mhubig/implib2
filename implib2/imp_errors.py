#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .imp_helper import _load_json


class ErrorsError(Exception):
    pass


# pylint: disable=too-few-public-methods
class Errors(object):

    def __init__(self, filename='imp_errors.json'):
        self._errors = _load_json(filename)

    def lookup(self, errno):
        try:
            return self._errors[str(errno)]
        except KeyError:
            raise ErrorsError("Unknown error number: {}".format(errno))
