import os, sys
import subprocess
import ast

from check.logger import i_log

log = i_log(level='DEBUG', name=__name__)


def _read_pattern_test_file(tests_folder):
    """
    Read test.py
    Return AST tree

    :param tests_folder:
    :return: ast tree
    """

    test_py_file_dir = tests_folder + os.sep + "tests\\"
    if os.path.exists(test_py_file_dir + os.sep + "test.py"):
        log.debug("Folder tests for current patters - exist: " + str(test_py_file_dir))

        raw_test_py = open(test_py_file_dir+"test.py", 'r')
        log.debug("Reading: " + test_py_file_dir + "test.py")

        try:
            raw_test_content = raw_test_py.read()
            test_tree = ast.parse(raw_test_content)
        except UnicodeDecodeError as unicode_err:
            print("Error: Unable to parse {!r}".format(str(unicode_err)))

        return test_tree
    else:
        log.warn("File test.py did not found. Please check it in path: " + str(test_py_file_dir))


def import_pattern_tests(tests_folder):
    """
    Get test.py tree with args from self.setupPatterns()


    :param tests_folder:
    :return: list of pattern to import for test
    """

    test_tree = _read_pattern_test_file(tests_folder)
    pattern_import_test = []

    # Walk in test.py file and get function arguments where import patterns lies:
    for node in ast.walk(test_tree):
        if isinstance(node, ast.Expr):
            if node.value.func.attr == "setupPatterns":
                for arg in node.value.args:
                    pattern_import_test.append(arg.s)

    return pattern_import_test


def query_pattern_tests(tests_folder):
    """
    Get test.py tree with args from self.setupPatterns()
    Now only RAW queries not with plus


    :param tests_folder:
    :return: list of queries to run in test
    """

    test_tree = _read_pattern_test_file(tests_folder)
    query_list = []

    # Walk in test.py file and get function arguments where import patterns lies:
    # TODO: Make walker to get all left and right values in loop.
    for node in ast.walk(test_tree):
        if isinstance(node, ast.ClassDef):
            # Get into the class with name:
            if node.name == "TestStandalone":
                # Pick each item from Class body
                for item in node.body:
                    # Check if this item is var assign:
                    if isinstance(item, ast.Assign):
                        # Check if this var is just a string:
                        if isinstance(item.value, ast.Str):
                            print(item.targets[0].id)
                            print(item.value.s)
                        # Check if this var is sum of vars and binary:
                        if isinstance(item.value, ast.BinOp):
                            plus = " + "
                            # print(item.targets[0].id)
                            print(vars(item.value))
                            operators = [item.value.left, item.value.op, item.value.right]

                            # print(item.value.left.left.left.id) # NULL_QUERY_2
                            # print(item.value.left.left.right.id) # GENERAL_QUERY
                            # print(item.value.left.right.id) # SMART_QUERY
                            # print(item.value.right.id) # NULL_QUERY_1

                            construct = item.targets[0].id + " = " + \
                                        item.value.left.left.left.id + plus + \
                                        item.value.left.left.right.id + plus + \
                                        item.value.left.right.id + plus + \
                                        item.value.right.id
                            print(construct)
                            print(operators)

    return query_list

