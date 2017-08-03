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



class GlobalLogic:

    def __init__(self, logging):

        self.logging = logging

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
            tpl_imports = TPLimports(log)
            import_included_modules = tpl_imports.import_modules(working_dir)
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

        parsable_args_set = parse_args.gather_args(known_args, extra_args)
        addm_args_set = parse_args.addm_args(known_args)

        return parsable_args_set, addm_args_set

    def make_function_set(self, known_args, extra_args):
        """
        Dummy.
        Will be used for functions set.

        :return:
        """
        log = self.logging

        full_path_args, addm_args_set = self.check_args_set(known_args, extra_args)
        print(full_path_args)
        print(addm_args_set)

        workspace = full_path_args['workspace']
        full_path = full_path_args['full_path']
        working_dir = full_path_args['working_dir']
        workspace = full_path_args['workspace']
        file_ext = full_path_args['file_ext']

        ssh = addm_args_set['ssh_connection']
        disco = addm_args_set['disco_mode']
        scan_hosts = addm_args_set['scan_hosts']
        tpl_vers = addm_args_set['tpl_vers']

        if file_ext == "tplpre":
            if known_args.I:
                log.debug("Argument for I-mport is True")
                mode = 'imports'
                preproc = self.make_preprocessor(workspace=workspace,
                                                 input_path=full_path,
                                                 output_path=working_dir,
                                                 mode=mode)

            if known_args.RI:
                log.debug("Argument for RI-mport is True")

                # Import tplpre's in recursive mode:
                # tpl_imports = TPLimports(log)
                # tpl_imports.import_modules(full_path_args['working_dir'])

                # After R imports are finish its work - run TPLPreprocessor on it
                mode = 'recursive_imports'
                input = full_path + "\\imports\\"
                output = working_dir + "\\imports\\"
                preproc = self.make_preprocessor(workspace=workspace,
                                                 input_path=input,
                                                 output_path=output,
                                                 mode=mode)
                print(preproc)

                # After TPLPreprocessor finished its work - run Syntax Check on folder imports


            if known_args.T:
                log.debug("Argument for T-ests is True")

                # Read test.py for queries and atc...
                test_read = TestRead(log)
                pattern_list = test_read.import_pattern_tests(working_dir)
                query_list = test_read.query_pattern_tests(working_dir)
                # print(query_list)
        else:
            log.info("This is not a DEV file.")

        # if ssh and working_dir:
        #
        #     log.debug("SHH is still there!")
        #     addm = AddmOperations(log, ssh)

    def make_preprocessor(self, workspace, input_path, output_path, mode):
        """

        :param args_set:
        :return:
        """

        log = self.logging
        preproc = Preproc(log).tpl_preprocessor(workspace, input_path, output_path, mode)

        return preproc
