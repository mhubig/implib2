#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

# I really prefer Markdown to reStructuredText. PyPi does not. This allows me
# to have things how I'd like, but not throw complaints when people are trying
# to install the package and they don't have pypandoc or the README in the
# right place. Inspired by: https://coderwall.com/p/qawuyq
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r", "")
except (IOError, ImportError):
    long_description = ''

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
    version='0.12.0',
    packages=find_packages(exclude=["tests"]),

    # include the *.yaml files
    package_data={
        'implib2': ['*.json'],
    },

    # required to use implib2
    install_requires=[
        "pyserial",
    ],

    # required to run setup.py
    setup_requires=[
        "pypandoc"
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
    long_description=long_description,
    license="LGPL",
    keywords="serial impbus imko",
    classifiers=CLASSIFIERS,
)
