import pytest  # noqa

import implib2 # noqa
from packaging.version import Version


class TestImplib2(object):

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_verion(self):
        assert Version(implib2.__version__)
