"""
This is script for use logical decisions based on args obtained.

Later I will add here scenarios.

    If file is .tplpre we need to
        - check imports and add if any (args based)
        - run TPLPreprocessor on it and check results (ALWAYS for tplpre but based or args (file|dir))
        - run Syntax check  (args based)
        - ask ADDM for ver and zip tpl folder (args based)
        - upload tpl folder into ADDM (args based)
        - start scan in mode: (args based)
        - check query (args based)
        - generate model file (args based)
        - generate used query file (args based)

"""

from check.parse_args import ArgsParse
from check.preproc import Preproc
from check.imports import TPLimports
from check.test_queries import TestRead
from check.upload import AddmOperations
from check.local_logic import LocalLogic

from check.syntax_checker import syntax_check, parse_syntax_result

# from TPLPreprocessor import TPLPreprocessor


class GlobalLogic:

    def __init__(self, logging, known_args, extra_args):
        # TODO: Make func sets and then execute each one by one in right order) or not (closure)
        # TODO: (ex above) - use to execute each function in right order right here

        self.logging = logging

        self.full_path_args, self.addm_args_set, self.operational_args = self.check_args_set(known_args, extra_args)

        log = self.logging
        if self.full_path_args:

            # print("PATH ARGS: "+str(self.full_path_args))

            self.workspace   = self.full_path_args['workspace']
            self.full_path   = self.full_path_args['full_path']
            self.working_dir = self.full_path_args['working_dir']
            self.workspace   = self.full_path_args['workspace']
            self.file_ext    = self.full_path_args['file_ext']

            log.debug("Arguments from -full_path are obtained and program will make decisions.")
        else:
            log.warn("Arguments from -full_path are'n obtained and program cannot make decisions.")

        if self.addm_args_set:

            # print("ADDM VM ARGS: "+str(self.addm_args_set))

            self.ssh        = self.addm_args_set['ssh_connection']
            self.disco      = self.addm_args_set['disco_mode']
            self.scan_hosts = self.addm_args_set['scan_hosts']
            self.tpl_vers   = self.addm_args_set['tpl_vers']

            log.debug("Arguments from -addm are obtained and program will make decisions.")
        else:
            log.warn("Arguments from -full_path are'n obtained and program cannot make decisions.")

        if self.operational_args:

            # print("OPERATIONS ARGS: "+str(self.operational_args))

            self.recursive_imports = self.operational_args['recursive_imports']
            self.usual_imports     = self.operational_args['usual_imports']
            self.read_test         = self.operational_args['read_test']

            log.debug("Arguments from -T, amd imports are obtained and program will make decisions.")
        else:
            log.warn("Arguments from -full_path are'n obtained and program cannot make decisions.")

    def check_file_extension(self, file_ext):
        """
        Based on file extension - describe further scenario with current file



        :param file_ext:
        :return:
        """

        log = self.logging

        # TODO: Compose set of functions filled with all
        # TODO: needed args for each scenario and return in to main module to execute.
        if file_ext == "tplpre":
            tpl_preproc = Preproc(log)

            log.debug("")
        elif file_ext == "tpl":
            log.debug("")
        elif file_ext == "py":
            log.debug("")
        elif file_ext == "dml":
            log.debug("")
        elif file_ext == "model":
            log.debug("")
        else:
            log.error("There is no file extension!")

    def check_args_set(self, known_args, extra_args):
        """
        This will check args set in input.
        Based on set of args - it will compose another set of functions.
        The set of functions will consist of all neded functions on order to execute.

        Example:
            - for usual way for tplpre with imports and pack of patterns:
                -- 1. Imports_(for all from current pattern + all recursive patterns),
                   2. TPLPreproc_(for all in imports folder),
                   3. SyntaxCheck_(for all in imports folder), -- This probably will be removed later with AST
                   4. AskADDM_(ADDM SSH connection - check supported tpl, working folder, save SSH session)
                   5. UploadPatterns_ (zip patterns for correspond tpl ver from ADDM - upload-activate)
                   6. StartScan_(start Discovery with options)
                   7. CheckScan_(Check when scan is finished and successful)
                   8. RunQuery_(Run Search SoftwareInstance or so and output result)
                   9. SaveResults_(save model file for SI and Query file for queries with results)
                   10. ...
            - for tpl usage (without Preproc or Syntax):
                -- 1. AskADDM_(ADDM SSH connection - check supported tpl, working folder, save SSH session)
                   2. UploadPatterns_ (zip patterns for correspond tpl ver from ADDM - upload-activate)
                   3. StartScan_(start Discovery with options)
                   4. CheckScan_(Check when scan is finished and successful)
                   5. RunQuery_(Run Search SoftwareInstance or so and output result)
                   6. SaveResults_(save model file for SI and Query file for queries with results)
                   7. ...
            - for test.py (or something like that) if will be added:
                -- 1. AskADDM_(ADDM SSH connection - check supported tpl, working folder, save SSH session)
                   2. StartTH_(start TestHarness in tku_patterns folder and output results)
                   3. ExecuteTest_(run test with set of options you send)
                   4. ValidateTests_(check something you need to)
                   5. This section not even planned yet, can be changed.

        :param args_set:
        :return:
        """
        log = self.logging

        parse_args = ArgsParse(log)

        parsable_args_set, operational_args = parse_args.gather_args(known_args, extra_args)
        addm_args_set = parse_args.addm_args(known_args)
        # print(parsable_args_set)

        return parsable_args_set, addm_args_set, operational_args

    def make_function_set(self):
        """
        This function will decide WHAT set of other functions to RUN -
        - based on arguments which was initialized in Class.
        So this mean - the execution process will run HERE and args -
        - will choose what behaviour to use.

        Will be used for functions set.

        :return:
        """
        log = self.logging
        preproc            = ''
        imports_f          = ''
        imports_t          = ''
        query_t            = ''
        syntax_check_f     = ''
        addm_check_f       = ''
        addm_upload_f      = ''
        addm_activate_f    = ''
        addm_start_scan_f  = ''
        addm_gather_data_f = ''
        addm_verify_data_f = ''
        addm_save_model_f  = ''

        if self.file_ext == "tplpre":
            if self.usual_imports:
                log.debug("Argument for imp IMPORT is True")

                preproc = self.make_preprocessor(workspace=self.workspace,
                                                 input_path=self.full_path,
                                                 output_path=self.working_dir,
                                                 mode="usual_imports")
            if self.recursive_imports:
                log.debug("Argument for r_imp RECURSIVE import is True")

                # Import tplpre's in recursive mode:
                imports_f = self.make_imports()

                # After R imports are finish its work - run TPLPreprocessor on it
                input = self.working_dir + "\\imports"
                output = self.working_dir + "\\imports"
                preproc = self.make_preprocessor(workspace=self.workspace,
                                                 input_path=input,
                                                 output_path=output,
                                                 mode="recursive_imports")
                # After TPLPreprocessor finished its work - run Syntax Check on folder imports

            if self.read_test:
                log.debug("Argument for TESTS read test file is True")

                # Read test.py for queries and atc...
                imports_t, query_t = self.make_test_read_patterns(), self.make_test_read_query()
            else:
                log.debug("There is no DEV arg.")

            functions_dict = {'import_patterns':       imports_f,
                              'prepcoc_patterns':      preproc,
                              'syntax_check':          syntax_check_f,
                              'addm_check_ssh':        addm_check_f,
                              'addm_upload_pattern':   addm_upload_f,
                              'addm_activate_pattern': addm_activate_f,
                              'addm_start_scan':       addm_start_scan_f,
                              'addm_gather_data':      addm_gather_data_f,
                              'addm_verify_data':      addm_verify_data_f,
                              'addm_save_model':       addm_save_model_f
                             }
        else:
            log.info("This is not a DEV file.")

        # if ssh and working_dir:
        #
        #     log.debug("SHH is still there!")
        #     addm = AddmOperations(log, ssh)

        return functions_dict

    def make_preprocessor(self, workspace, input_path, output_path, mode):
        """

        :param mode:
        :param output_path:
        :param input_path:
        :param workspace:
        :param args_set:
        :return:
        """
        log = self.logging

        def pre_processing():
            preproc = Preproc(log)
            preproc.tpl_preprocessor(workspace, input_path, output_path, mode)
        return pre_processing

    def make_imports(self):
        """
        Based or arguments - decide which import will run.
        Or nothing to run at all.

        :return:
        """
        log = self.logging

        def importer():
            tpl_imports = TPLimports(log, self.full_path_args)
            # Now I don't need args because class was initialized with args above:
            tpl_imports.import_modules()
        return importer

    def make_test_read_patterns(self):
        """
        Read test.py for queries and atc...
        :return: funcs for each search
        """
        log = self.logging

        def test_patterns():
            test_read = TestRead(log)
            test_read.import_pattern_tests(self.working_dir)
        # return test_read.import_pattern_tests(self.working_dir)
        return test_patterns

    def make_test_read_query(self):
        log = self.logging

        def test_queries():
            test_read = TestRead(log)
            test_read.query_pattern_tests(self.working_dir)
        # return test_read.query_pattern_tests(self.working_dir)
        return test_queries

    def addm_test(self):
        log = self.logging