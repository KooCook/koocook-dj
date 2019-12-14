import doctest

from koocook_core.support import utils


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(utils))
    # add doctests in support/utils.py
    return tests
