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


def _normalize(filename):
    """ .. function:: _normalize(filename)

    Prepends the filename with the path pointing to the main file.

    :type filename: string
    :rtype: string
    """
    import os
    abs_path = os.path.abspath(__file__)
    dir_name = os.path.dirname(abs_path)
    return os.path.join(dir_name, filename)


def _load_json(filename):
    """ .. funktion:: _load_json(filename)

    Reads the spezific json file.

    :type filename: string
    :rtype: dict
    """
    import json
    filename = _normalize(filename)
    with open(filename) as js_file:
        return json.load(js_file)


def _flp2(number):
    """ .. funktion:: _flp2(number)

    Rounds x to the largest z | z=2**n.

    :type number: int
    :rtype: int
    """
    number |= (number >> 1)
    number |= (number >> 2)
    number |= (number >> 4)
    number |= (number >> 8)
    number |= (number >> 16)
    return number - (number >> 1)


def _imprange(low, high):
    """ .. funktion:: _imprange(low, high)

    Takes a serial number range and returns the range address and the marker
    which can be compined (range + maker) to the broadcast address for the
    given range.

    :type low: int
    :type high: int
    :rtype: tuble

    """
    pfix = low ^ high
    mark = _flp2(pfix)
    fill = mark | (mark - 1)
    mask = fill ^ 0xFFFFFF
    return low & mask, mark
