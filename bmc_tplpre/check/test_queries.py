import os, sys
import subprocess

from check.logger import i_log

log = i_log(level='DEBUG', name=__name__)


def import_pattern_tests(tests_folder):
    """
    Importing test.py file for current pattern and use settings and queries from it.

    :param tests_folder:
    :return:
    """

    test_py_file_dir = tests_folder + os.sep + "tests\\"
    if os.path.exists(test_py_file_dir):
        log.debug("Folder tests for current patters - exist: " + str(test_py_file_dir))

        sys.path.insert(1, os.path.join(sys.path[0], test_py_file_dir))

        from test import TestStandalone

        test_standalone = TestStandalone()

        query = test_standalone.GENERAL_QUERY

        log.info("test.py query: " + str(query))

    else:
        log.warn("There is no 'tests' for this pattern!")
