"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import os
import ast
import re
import logging
log = logging.getLogger("check.logger")


class TestRead:

    def __init__(self):
        # TODO: Allow to parse dev_tests and dml/ip data to use in TH mode

        self.pattern_import_all_r = re.compile('from\s+(.+?)\s+import')
        self.core_from_wd_r = re.compile("\S+tku_patterns\\\CORE\\\\")

        self.tkn_core = os.environ.get("TKN_CORE")

    @staticmethod
    def _read_test(working_dir):
        """
        Read test.py
        Return AST tree

        :param working_dir: where pattern lies
        :return: ast tree
        """
        test_py_file_dir = working_dir + os.sep + "tests\\"
        if os.path.exists(test_py_file_dir + os.sep + "test.py"):
            log.debug("Folder tests for current patters - exist: " + str(test_py_file_dir))

            raw_test_py = open(test_py_file_dir+"test.py", 'r')
            log.debug("Reading: " + test_py_file_dir + "test.py")

            try:
                raw_test_content = raw_test_py.read()
                test_tree = ast.parse(raw_test_content)
                return test_tree
            except UnicodeDecodeError as unicode_err:
                log.critical("Error: Unable to parse {!r}".format(str(unicode_err)))

        else:
            log.warning("File test.py did not found. Please check it in path: " + str(test_py_file_dir))

    def import_pattern_tests(self, working_dir):
        """
        Get test.py tree with args from self.setupPatterns()
        Send list of patterns to import logic of imports.py

        :param working_dir: str: path to patterns folder.
        :return: list of pattern to import for test
        """
        test_tree = self._read_test(working_dir)
        pattern_import_test = []
        log.debug("Reading import patterns from test.py")

        if test_tree:
            # Walk in test.py file and get function arguments where import patterns lies:
            for node in ast.walk(test_tree):
                '''
                This is to extract list of patterns from test.py file.
                In first case in modern test.py it will be a tuple which can be appended as it is.
                In second case in older version of test.py this is a list, so we adding each from it. 
                '''
                if isinstance(node, ast.Call):
                    node_func = node.func
                    if isinstance(node_func, ast.Attribute):
                        if node_func.attr == "setupPatterns":
                            node_args = node.args
                            # DEBUG: Iter all nodes
                            # node_iter = ast.iter_fields(node)
                            # for i in node_iter:
                            #     print(i)
                            for arg in node_args:
                                patterns = ast.literal_eval(arg)
                                pattern_import_test.append(patterns)
                                # pattern_import_test.append(arg.s)
                        if node_func.attr == "preProcessTpl":
                            node_args = node.args
                            # DEBUG: Iter all nodes
                            # node_iter = ast.iter_fields(node)
                            # for i in node_iter:
                            #     print(i)
                            for arg in node_args:
                                patterns = ast.literal_eval(arg)
                                for pattern in patterns:
                                    pattern_import_test.append(pattern)
            # make list of self.setupPatterns() to abs path to each pattern:

            if pattern_import_test:
                # full_test_patterns_path = self.test_patterns_list(pattern_import_test, working_dir, tku_patterns)
                full_test_patterns_path = self.test_patterns_list(pattern_import_test, working_dir)

                return full_test_patterns_path
        else:
            log.warning("Cannot get test patterns. "
                        "File test.py is not found or not readable in this path: "+str(working_dir))

    def query_pattern_tests(self, working_dir):
        """
        Get test.py tree with args from self.setupPatterns()
        Now only RAW queries not with plus
        https://ruslanspivak.com/lsbasi-part7/
        https://stackoverflow.com/questions/9425409/python-ast-package-traversing-object-hierarchies

        :param working_dir:
        :return: list of queries to run in test
        """

        test_tree = self._read_test(working_dir)
        query_list = []

        # Walk in test.py file and get function arguments where import patterns lies:
        # TODO: Make walker to get all left and right values in loop.
        # https://ruslanspivak.com/lsbasi-part7/
        # https://stackoverflow.com/questions/9425409/python-ast-package-traversing-object-hierarchies
        if test_tree:
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
    
                                Will try to parse it later, after making 
                                some kind of construction to get all vars on right order.
                                https://ruslanspivak.com/lsbasi-part7/
                            '''
                            # if isinstance(item.value, ast.BinOp):
                            #     operators = [item.value.left, item.value.op, item.value.right]
                            #     log.debug("This is Binary Options. I do not parse it now, sorry. " + str(operators))
            return query_list
        else:
            log.warning("Cannot get test queries. "
                        "File test.py is not found or not readable in this path: "+str(working_dir))

    def test_patterns_list(self, setup_patterns, working_dir):
        """
        Get raw list 'self.setupPatterns' from test.py and make it full path to each pattern

        :param setup_patterns: raw list of pattern items from test.py
        :param working_dir: working dir of current pattern
        :return:
        """
        log.debug("Composing paths to patterns from test.py")
        patten_abs_path_list = []

        test_py_file_dir = working_dir + os.sep + "tests\\"
        for p in setup_patterns:
            # Normalize pattern paths:
            pattern_path = os.path.normpath(p)
            normal_pattern_path = os.path.join(test_py_file_dir, pattern_path)
            # Join and verify pattern path for each composed path:
            abs_pattern_path = os.path.abspath(normal_pattern_path)
            if os.path.exists(abs_pattern_path):
                if abs_pattern_path not in patten_abs_path_list:
                    patten_abs_path_list.append(abs_pattern_path)
            else:
                log.warning("Cannot find file in path"+str(abs_pattern_path))

        return patten_abs_path_list


