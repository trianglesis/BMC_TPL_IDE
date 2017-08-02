import os
import ast
import re


class TestRead:

    def __init__(self, logging):

        self.logging = logging
        self.pattern_import_all_r = re.compile('from\s+(.+?)\s+import')
        self.core_from_wd_r = re.compile("\S+tku_patterns\\\CORE\\\\")

        self.tkn_core = os.environ.get("TKN_CORE")

    def _read_pattern_test_file(self, tests_folder):
        """
        Read test.py
        Return AST tree

        :param tests_folder:
        :return: ast tree
        """
        log = self.logging
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

    def import_pattern_tests(self, tests_folder):
        """
        Get test.py tree with args from self.setupPatterns()


        :param tests_folder:
        :return: list of pattern to import for test
        """
        log = self.logging
        test_tree = self._read_pattern_test_file(tests_folder)
        pattern_import_test = []

        # Walk in test.py file and get function arguments where import patterns lies:
        for node in ast.walk(test_tree):
            if isinstance(node, ast.Expr):
                if node.value.func.attr == "setupPatterns":
                    for arg in node.value.args:
                        pattern_import_test.append(arg.s)

        return pattern_import_test

    def query_pattern_tests(self, tests_folder):
        """
        Get test.py tree with args from self.setupPatterns()
        Now only RAW queries not with plus
        https://ruslanspivak.com/lsbasi-part7/
        https://stackoverflow.com/questions/9425409/python-ast-package-traversing-object-hierarchies

        :param tests_folder:
        :return: list of queries to run in test
        """
        log = self.logging

        test_tree = self._read_pattern_test_file(tests_folder)
        query_list = []

        # Walk in test.py file and get function arguments where import patterns lies:
        # TODO: Make walker to get all left and right values in loop.
        # https://ruslanspivak.com/lsbasi-part7/
        # https://stackoverflow.com/questions/9425409/python-ast-package-traversing-object-hierarchies
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
                                query_name = item.targets[0].id
                                query_body = item.value.s
                                query = {'query_name': query_name, 'query_body': query_body}
                                query_list.append(query)
                        '''
                            When query has two or more binary options:
                            MEGA_QUERY = NULL_QUERY_2 + GENERAL_QUERY + SMART_QUERY + NULL_QUERY_1

                            Will try to parse it later, after making some kind of construction to get all vars on right order.
                            https://ruslanspivak.com/lsbasi-part7/
                        '''
                        # if isinstance(item.value, ast.BinOp):
                        #     operators = [item.value.left, item.value.op, item.value.right]
                        #     log.debug("This is Binary Options. I do not parse it now, sorry. " + str(operators))

        return query_list


