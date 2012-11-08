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

from setuptools import setup, find_packages

setup(
        name = 'IMPLib2',
        version = 'release-0.4.0',
        packages = find_packages(),

        # Include the *.yaml files
        package_data = {
            'implib2': ['*.yaml'],
        },

        # Install or upgrade the dependencies
        install_requires = [
            'PySerial>=2.6',
            'PyYAML>=3.10',
            'SQLAlchemy>=0.7.9',
        ],

        # metadata for upload to PyPI
        author = 'Markus Hubig',
        author_email = 'mhubig@imko.de',
        url = 'https://bitbucket.org/imko/implib2',
        description = 'Python implementation of the IMPBUS-2 data transmission protocol.',
        license = "LGPL",
        keywords = "serial impbus imko"
)
