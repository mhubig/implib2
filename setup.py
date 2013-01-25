#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

import os
from setuptools import setup, find_packages

# Utility function to read the README file, used for the long_description.
# It's nice, because now 1) we have a top level README file and 2) it's
# easier to type in the README file than to put a raw string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

CLASSIFIERS = filter(None, map(str.strip,
"""
"Development Status :: 4 - Beta",
"Topic :: Software Development :: Libraries",
"Intended Audience :: Developers",
"Programming Language :: Python :: 2.7",
"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)"
""".splitlines()))

setup(
        name = 'IMPLib2',
        version = 'release-0.8.0',
        packages = find_packages(exclude=["tests"]),

        # Include the *.yaml files
        package_data = {
            'implib2': ['*.json'],
        },

        # Install or upgrade the dependencies
        install_requires = [
            'PySerial>=2.6',
        ],

        # metadata for upload to PyPI
        author = 'Markus Hubig',
        author_email = 'mhubig@imko.de',
        url = 'https://bitbucket.org/imko/implib2',
        description = ("Python implementation of the IMPBUS-2 data "
            "transmission protocol."),
        long_description=read('README.md'),
        license = "LGPL",
        keywords = "serial impbus imko",
        classifiers = CLASSIFIERS,
)
