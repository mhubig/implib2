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

import re
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# The following snippet is taken directly from the tox documentation:
class Tox(TestCommand):

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


# Extracts the version information from the init file.
def get_version():
    return re.search(
        r"""__version__\s+=\s+(?P<quote>['"])(?P<version>.+?)(?P=quote)""",
        open('implib2/__init__.py').read()).group('version')


CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Topic :: Software Development :: Libraries",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 2.7",
    ("License :: OSI Approved :: GNU Lesser "
     "General Public License v3 or later (LGPLv3+)"),
]

setup(
    name='IMPLib2',
    version='0.11.1',
    packages=find_packages(exclude=["tests"]),

    # include the *.yaml files
    package_data={
        'implib2': ['*.json'],
    },

    # install or upgrade the dependencies
    install_requires=[
        "pyserial",
    ],

    # testing with tox
    tests_require=['tox'],
    cmdclass={'test': Tox},

    # metadata for upload to PyPI
    author='Markus Hubig',
    author_email='mhubig@imko.de',
    url='https://github.com/mhubig/implib2',
    description=("Python implementation of the IMPBUS-2 "
                 "data transmission protocol."),
    long_description=open("README.rst").read(),
    license="LGPL",
    keywords="serial impbus imko",
    classifiers=CLASSIFIERS,
)
