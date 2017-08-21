"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.


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
import os
from check.parse_args import ArgsParse
from check.preproc import Preproc
from check.imports import TPLimports
from check.test_queries import TestRead
from check.upload import AddmOperations
from check.syntax_checker import SyntaxCheck
from check.local_logic import LocalLogic


class GlobalLogic:

    def __init__(self, logging, known_args, extra_args):
        # TODO: Make func sets and then execute each one by one in right order) or not (closure)
        # TODO: (ex above) - use to execute each function in right order right here
        # TODO: LATER: Switch to **kwargs because I mostly use sets of options!

        self.logging = logging

        self.full_path_args, self.addm_args_set, self.operational_args = self.check_args_set(known_args, extra_args)

        log = self.logging
        if self.full_path_args:
            '''
            PATH ARGS: {'file_name': 'BMCRemedyARSystem', 
                        'file_ext': 'tplpre', 
                        'workspace': 'd:\\perforce', 
                        'SupportingFiles_t': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles', 
                        'tkn_sandbox_t': 'd:\\perforce\\addm\\tkn_sandbox', 
                        'MIDDLEWAREDETAILS_t': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS', 
                        'tku_patterns_t': 'd:\\perforce\\addm\\tkn_main\\tku_patterns', 
                        'CORE_t': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE', 
                        'pattern_folder': 'BMCRemedyARSystem', 
                        'working_dir': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem', 
                        'buildscripts_t': 'd:\\perforce\\addm\\tkn_main\\buildscripts', 
                        'DBDETAILS_t': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS\\Database_Structure_Patterns', 
                        'full_path': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem\\BMCRemedyARSystem.tplpre', 
                        'tkn_main_t': 'd:\\perforce\\addm\\tkn_main'}

            '''

            print("PATH ARGS: "+str(self.full_path_args))

            self.tku_patterns_t = self.full_path_args['tku_patterns_t']
            self.CORE_t         = self.full_path_args['CORE_t']
            self.workspace      = self.full_path_args['workspace']
            self.full_path      = self.full_path_args['full_path']
            self.working_dir    = self.full_path_args['working_dir']
            self.workspace      = self.full_path_args['workspace']
            self.file_ext       = self.full_path_args['file_ext']

            log.debug("Arguments from -full_path are obtained and program will make decisions.")
        else:
            log.warn("Arguments from -full_path are'n obtained and program cannot make decisions.")

        if self.addm_args_set:
            '''
            ADDM VM ARGS: {'tpl_folder': 'tpl113', 
                           'dev_vm_check': False, 
                           'scan_hosts': '172.25.144.95, 172.25.144.39', 
                           'disco_mode': 'record', 
                           'tpl_vers': '1.13', 
                           'addm_prod': 'Bobblehat', 
                           'ssh_connection': <paramiko.client.SSHClient object at 0x0000000003674E10>, 
                           'addm_ver': '11.1'}
            '''

            print("ADDM VM ARGS: "+str(self.addm_args_set))

            self.ssh            = self.addm_args_set['ssh_connection']
            self.disco          = self.addm_args_set['disco_mode']
            self.scan_hosts     = self.addm_args_set['scan_hosts']
            self.tpl_vers       = self.addm_args_set['tpl_vers']
            self.tpl_folder     = self.addm_args_set['tpl_folder']
            self.scan_hosts     = self.addm_args_set['scan_hosts']
            self.dev_vm_check   = self.addm_args_set['dev_vm_check']
            self.dev_vm_path    = self.addm_args_set['dev_vm_path']

            log.debug("Arguments from -addm are obtained and program will make decisions.")
        else:
            log.warn("Arguments from -addm_args_set are'n obtained and program cannot make decisions.")

        if self.operational_args:
            '''
            OPERATIONS ARGS: {'usual_imports': False, 
                              'recursive_imports': True, 
                              'read_test': False}
            '''

            print("OPERATIONS ARGS: "+str(self.operational_args))

            self.recursive_imports = self.operational_args['recursive_imports']
            self.usual_imports     = self.operational_args['usual_imports']
            self.read_test         = self.operational_args['read_test']

            if self.recursive_imports:
                log.debug("Argument recursive imports is true - will find imports in TKN_CORE if exist!")
            if self.usual_imports:
                log.debug("Argument usual imports is true - will find imports in TKN_CORE if exist!")
            if self.read_test:
                log.debug("Argument test read is true - will find imports from test.py "
                          "(recursive always) in TKN_CORE if exist!")
        else:
            self.recursive_imports = False
            self.usual_imports     = False
            self.read_test         = False

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
        # Init empty:
        parsable_args_set = dict()
        addm_args_set = dict()
        operational_args = dict()
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
        # Init empty:

        preproc_f          = False
        imports_f          = False
        imports_t          = False
        query_t            = False
        syntax_check_f     = False
        addm_check_f       = False
        addm_upload_f      = False
        addm_activate_f    = False
        addm_start_scan_f  = False
        addm_gather_data_f = False
        addm_verify_data_f = False
        addm_save_model_f  = False

        addm_operations_dict = {
                                'addm_check_ssh':        addm_check_f,
                                'addm_upload_pattern':   addm_upload_f,
                                'addm_activate_pattern': addm_activate_f,
                                'addm_start_scan':       addm_start_scan_f,
                                'addm_gather_data':      addm_gather_data_f,
                                'addm_verify_data':      addm_verify_data_f,
                                'addm_save_model':       addm_save_model_f
                                }

        local_functions_dict = {
                          'parse_tests_patterns':  imports_t,
                          'parse_tests_queries':   query_t,
                          'import_patterns':       imports_f,
                          'prepcoc_patterns':      preproc_f,
                          'syntax_check':          syntax_check_f
                         }

        # TODO Wisely add conditions to decide what logic to use when file is different ext or from diff places.
        # TODO Syntax check for tplpre, tpl, and optionally switch of if debug run.
        if self.file_ext == "tplpre":

            """
            Run developments procedures only if this is tplpre file.
            Import modules from active pattern + extra from tests.
            Run TPLPreprocessor on result folder or file.
            Ask ADDM for version.
            Check syntax for correspond tpl version.
            Upload to ADDM zip of patterns.
            Start scan.
            Generate data, dml, models etc.
            """
            # NORMAL IMPORTS
            if self.usual_imports:
                """
                When you don't want to import whole set of modules but only ones are used in current pattern.
                """

                preproc_f = self.make_preprocessor(workspace=self.workspace,
                                                   input_path=self.full_path,
                                                   output_path=self.working_dir,
                                                   mode="usual_imports")

                syntax_check_f = self.make_syntax_check(self.working_dir)

            # RECURSIVE MODE:
            elif self.recursive_imports:
                """
                When you want to import modules for each pattern in working dir and each it recursive.
                """
                # Import tplpre's in recursive mode:
                imports_f = self.make_imports(extra_patterns=None)

                # After R imports are finish its work - run TPLPreprocessor on it
                input = self.working_dir + "\\imports"
                output = self.working_dir + "\\imports"
                preproc_f = self.make_preprocessor(workspace=self.workspace,
                                                   input_path=input,
                                                   output_path=output,
                                                   mode="recursive_imports")
                # After TPLPreprocessor finished its work - run Syntax Check on folder imports
                syntax_check_f = self.make_syntax_check(output)

            # TESTs + RECURSIVE MODE:
            elif self.read_test and self.recursive_imports:
                """
                As recursive imports but also includes patterns from self.setupPatterns from test.py
                """
                # Read test.py and extract query for future validation after addm scan and save model:
                query_t = self.make_test_read_query()

                # Read test.py and extract list of patterns from self.setupPatterns
                imports_t = TestRead(log).import_pattern_tests(self.working_dir, self.tku_patterns_t)

                # Import tplpre's in recursive mode with extras from test.py:
                imports_f = self.make_imports(imports_t)

                # After R imports are finish its work - run TPLPreprocessor on it
                input = self.working_dir + "\\imports"
                output = self.working_dir + "\\imports"
                preproc_f = self.make_preprocessor(workspace=self.workspace,
                                                   input_path=input,
                                                   output_path=output,
                                                   mode="recursive_imports")

                # After TPLPreprocessor finished its work - run Syntax Check on folder imports
                syntax_check_f = self.make_syntax_check(output)

            # SOLO MODE:
            else:
                """
                If file is tplre - but no dev args found.
                This can be an alone tplpre from folder Download for example.
                In this case I will try to ask windows PATH for TKN_CORE or 
                run p4 command to obtain workspace path and compose dev paths to all I need to run and use.  
                """
                log.info("There are no dev arguments found for Test read, or imports, or recursive imports. "
                         "Using as standalone tplpre and trying to search TKN_CORE!")

                preproc_f = self.make_preprocessor(workspace=self.workspace,
                                                   input_path=self.full_path,
                                                   output_path=self.working_dir,
                                                   mode="solo_mode")
                # No SYNTAX CHECK should be used in solo mode, because there is no imported modules in results folder!
                # syntax_check_f = self.make_syntax_check(self.working_dir)

            local_functions_dict = {
                              'parse_tests_patterns':  imports_t,
                              'parse_tests_queries':   query_t,
                              'import_patterns':       imports_f,
                              'prepcoc_patterns':      preproc_f,
                              'syntax_check':          syntax_check_f
                             }
        elif self.file_ext == "tpl":
            """
            Here: if you just editing usual tpl file - you don't need to tpreproc it.
            Probably imports and recursive imports SHOULD NOT be implemented for usual tpl.
            
            NOTE: There is a logical problem:
            - if tpl file is editing - does it mean - I need to find imports for it?
                - if yes - so there should be path to each import file which I can follow, but there is no prognoses-able
                    way to obtain this path. This means - that if we are editing single TPL file - we just want to 
                    check syntax and upload it to ADDM "as is"!
                    Single TPL file will be uploaded. Or folder with them?
                    Single TPL file cannot be syntax checked because it require imports!
                 
            """
            log.info("This is not a DEV file.")

        # TODO: Simultaneously check ADDM options and compose dict of possible options and scenarios.
        # TODO: Do not forget about syntax checks!
        if self.ssh and self.workspace:
            '''
            All pattern actions should be finished before I came here: Imports, Preproc, Syntax.
            
            If SSH connetsion is present - then ADDM was checked and I have a set of arguments to further use:

                if dev_vm with HGFS shares - compose remote path based on local (they are the same!) and
                    NOT UPLOAD files - but activate patterns with path which were composed here.
                if workspace then local dev path is confirmed
                
                if not dev_vm with HGFS - just use (created) hardcoded dev path as: /usr/tideway/TKU/Tpl_DEV/ and
                    upload files via SFTP
                if workspace then local dev path is confirmed
                
                if not workspace then local dev path is not found an upload path should be /usr/tideway/TKU/Tpl_DEV/
                    and ignore HGFS even if it was found
             
            '''

            if self.dev_vm_check:
                '''
                If ADDM has in its FS paths to local tku like: .host:/tku_patterns/CORE/
                       88G   48G   41G  54% /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE
                So I can use SSH commands and not upload anything from dev paths.
                '''
                log.info("ADDM: Is working in dev mode with HGFS confirmed. "
                         "I will compose path based on tkn_main logic.")

                local_logic = LocalLogic(log)
                addm_working_dir = local_logic.addm_compose_paths(dev_vm_path=self.dev_vm_path,
                                                                  pattern_folder=self.full_path_args['pattern_folder'])

                '''
                Preproc result folder is consist of working path and tplver 
                from addm and may have IMPORTS subdir or not based on args.
                '''
                if self.usual_imports or self.recursive_imports:
                    '''
                    Path to result is the path of imported, preprocessed and tested patterns forder in local system
                    and this path like it mirrored in remote system with HGFS.
                    '''
                    log.debug("DEV IMPORTS to addm: Making zip from imported patterns, activating them.")

                    # Possible path to local results folder and remote mirror:
                    path_to_result = self.full_path_args['working_dir']+os.sep+"imports"+os.sep+self.tpl_folder+os.sep
                    path_to_result_remote = addm_working_dir+"/imports/"+self.tpl_folder
                    zip_mirror = path_to_result_remote+"/"+self.full_path_args['pattern_folder'] + '.zip'

                    # Making function obj for ZIP
                    addm_upload_f = self.make_zip(path_to_result)

                    # Use zip path to start activation process with path composed for mirror addm FS:
                    addm_activate_f = self.activate_local_zip(zip_mirror)

                    if self.scan_hosts and self.disco:
                        '''
                            Check when we use arguments with 
                                'scan_hosts': '172.25.144.95, 172.25.144.39', and 
                                'disco_mode': 'record'
                            Use them for execute commands after upload activated and further use for DML and RecData gathering.
                        '''
                        log.info("ADDM: Scan mode arguments confirmed and will be used for scenario act.")

                    addm_operations_dict = {
                                            'addm_check_ssh':        addm_check_f,
                                            'addm_upload_pattern':   addm_upload_f,
                                            'addm_activate_pattern': addm_activate_f,
                                            'addm_start_scan':       addm_start_scan_f,
                                            'addm_gather_data':      addm_gather_data_f,
                                            'addm_verify_data':      addm_verify_data_f,
                                            'addm_save_model':       addm_save_model_f
                                            }

                elif not self.usual_imports and not self.recursive_imports:
                    '''
                    Just use full path to pattern tpl result and upload it to ADDM via SSH then activate.
                    '''
                    log.debug("DEV SOLO Pattern: activating local pattern in remote system.")
                    rem_patt = addm_working_dir+"/"+self.tpl_folder+"/" + self.full_path_args['file_name']+".tpl"
                    addm_activate_f = self.activate_local_zip(rem_patt)

                    addm_operations_dict = {
                                            'addm_check_ssh':        addm_check_f,
                                            'addm_upload_pattern':   addm_upload_f,
                                            'addm_activate_pattern': addm_activate_f,
                                            'addm_start_scan':       addm_start_scan_f,
                                            'addm_gather_data':      addm_gather_data_f,
                                            'addm_verify_data':      addm_verify_data_f,
                                            'addm_save_model':       addm_save_model_f
                                            }

                if self.scan_hosts and self.disco:
                    '''
                        Check when we use arguments with 
                            'scan_hosts': '172.25.144.95, 172.25.144.39', and 
                            'disco_mode': 'record'
                        Use them for execute commands after upload activated and further use for DML and RecData gathering.
                    '''
                    log.info("ADDM: Scan mode arguments confirmed and will be used for scenario act.")

            elif not self.dev_vm_check:
                '''
                When ADDM VM shares was not confirmed - I will upload all 
                active files into dev dir: /usr/tideway/TKU/Tpl_DEV/
                This dir will be created if not exist on args check stage.
                
                Use logic from if self.dev_vm_check: but with remote hardcoded path.
                '''
                log.info("ADDM: Is not working in dev mode, HGFS is not confirmed. "
                         "I will upload files into /usr/tideway/TKU/Tpl_DEV/ folder via SFTP.")

                # TODO: COpy logic from if self.usual_imports or self.recursive_imports

                if self.scan_hosts and self.disco:
                    '''
                        Check when we use arguments with 
                            'scan_hosts': '172.25.144.95, 172.25.144.39', and 
                            'disco_mode': 'record'
                        Use them for execute commands after upload activated and further use for DML and RecData gathering.
                    '''
                    log.info("ADDM: Scan mode arguments confirmed and will be used for scenario act.")

        elif self.ssh and not self.workspace:
            '''
            When local workspace was not confirmed and paths to %workspace%\\addm\\tkn_main\\tku_patterns\\..
            cannot be composed - I can only upload current files via SFTP to usual dev path: /usr/tideway/TKU/Tpl_DEV/
            This dir will be created if not exist - on args check stage.
            '''
            log.info("ADDM: Workspace path was not found and cannot be composed, so I will upload any active files"
                     "into /usr/tideway/TKU/Tpl_DEV/ folder via SFTP.")

            if self.scan_hosts and self.disco:
                '''
                    Check when we use arguments with 
                        'scan_hosts': '172.25.144.95, 172.25.144.39', and 
                        'disco_mode': 'record'
                    Use them for execute commands after upload activated and further use for DML and RecData gathering.
                '''
                log.info("ADDM: Scan mode arguments confirmed and will be used for scenario act.")

        return local_functions_dict, addm_operations_dict

    def remote_func_set(self):
        """
        Maybe better to verify first if local functions ready?

        :return:
        """

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

    def make_imports(self, extra_patterns):
        """
        Based or arguments - decide which import will run.
        Or nothing to run at all.

        :return:
        """
        log = self.logging

        def importer():
            tpl_imports = TPLimports(log, self.full_path_args)
            # Now I don't need args because class was initialized with args above:
            tpl_imports.import_modules(extra_patterns)
        return importer

    def make_test_read_patterns(self):
        """
        Read test.py for queries and atc...
        :return: funcs for each search
        """
        log = self.logging

        def test_patterns():
            test_read = TestRead(log)
            patterns = test_read.import_pattern_tests(self.working_dir, self.tku_patterns_t)
            return patterns
        # return test_read.import_pattern_tests(self.working_dir)
        return test_patterns

    def make_test_read_query(self):
        log = self.logging

        def test_queries():
            test_read = TestRead(log)
            test_read.query_pattern_tests(self.working_dir)
        # return test_read.query_pattern_tests(self.working_dir)
        return test_queries

    def make_syntax_check(self, working_dir):
        """
        Run LOCAL syntax check procedure in selected folders or files.
        Can run ONLY when imports from patter are also in the same folder.
        Should be ignored in SOLO MODE.

        :return:
        """
        log = self.logging

        def syntax_chek():
            syntax = SyntaxCheck(log)
            syntax.syntax_check(working_dir)

        return syntax_chek

    def addm_test(self):
        """
        Compose ADDM ssh functions: upload, scan, verify and etc.
        There SHOULD NOT be any checks which was made in parse_args as initial!
        Put here only file/upload checks or etc.

        :return:
        """
        log = self.logging

        def addm_ssh_tpl_version():
            print(self.ssh)
            print(self.disco)
            print(self.scan_hosts)
            print(self.tpl_vers)

        return addm_ssh_tpl_version

    def make_zip(self, path_to_result):
        """
        Closure for zipper.
        Make zip for local folder!
        :return: zipper func
        """
        log = self.logging

        def zipper():
            local_logic = LocalLogic(log)
            # Zip local processed files and return path to zip on local and name if zip for addm mirror FS:
            local_logic.make_zip(path_to_result, self.full_path_args['pattern_folder'])

        return zipper

    def activate_local_zip(self, zip_mirror):
        """
        Closure for pattern activation.
        Activate only on mirror FS on ADDM!
        :return: activate patterns func
        """
        log = self.logging

        def activate():
            addm = AddmOperations(log, self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm.activate_knowledge(zip_mirror, self.full_path_args['pattern_folder'])

        return activate

    def upload_remote(self, local_file):
        """
        Closure for pattern upload on remote addm via SFTP.
        IN PROGRESS!
        :return: activate patterns func
        """
        log = self.logging

        def activate():
            addm = AddmOperations(log, self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm.upload_knowledge(local_file, self.full_path_args['pattern_folder'])

        return activate

    def activate_remote(self, remote_path):
        """
        Activate remote uploaded zip of patterns.
        Give me remote path to zip file which was (should be) uploaded before

        IN PROGRESS!
        :zip_remote: remote path to uploaded ZIP!
        :return: activate patterns func
        """
        log = self.logging

        def activate():
            addm = AddmOperations(log, self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm.activate_knowledge(remote_path, self.full_path_args['pattern_folder'])

        return activate
