"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.


This is script for use logical decisions based on args obtained.

Later I will add here scenarios.

    If file is .tplpre I need to
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
from check.scan import AddmScan


class GlobalLogic:

    def __init__(self, **kwargs):

        logging = kwargs['logging']
        self.logging = logging
        log = self.logging

        # Get all available arguments in three sets based on its type:
        self.full_path_args, \
        self.operational_args, \
        self.addm_args_set = self.check_args_set(known_args = kwargs['known_args'],
                                                 extra_args = kwargs['extra_args'])

        # Check args in init module to furter assign on function bodies:
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
            self.workspace      = self.full_path_args['workspace']
            self.full_path      = self.full_path_args['full_path']
            self.working_dir    = self.full_path_args['working_dir']

            log.debug("Full path arguments are set. It will be used to choose programm working scenario.")
        else:
            log.debug("No full path arguments are set. I can do nothing with this.")

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

            # print("ADDM VM ARGS: "+str(self.addm_args_set))
            self.ssh            = self.addm_args_set['ssh_connection']
            self.tpl_folder     = self.addm_args_set['tpl_folder']
            self.dev_vm_path    = self.addm_args_set['dev_vm_path']

            log.debug("ADDM arguments are gathered from addm host. "
                      "It will be used to choose programm working scenario.")
        else:
            log.debug("ADDM arguments are gathered or wasn't set. Programm will work on local mode.")

        if self.operational_args:
            '''
            OPERATIONS ARGS: {'usual_imports': False, 
                              'recursive_imports': True, 
                              'read_test': False}
            '''

            # print("OPERATIONS ARGS: "+str(self.operational_args))

            self.recursive_imports = self.operational_args['recursive_imports']
            self.usual_imports     = self.operational_args['usual_imports']
            self.read_test         = self.operational_args['read_test']

            if self.recursive_imports and not self.usual_imports and not self.read_test:
                log.debug("Recursive imports used - I will find and copy any imports I found in TKN_CORE.")

            elif self.usual_imports and not self.recursive_imports and not self.read_test:
                log.debug("Usual imports used - TPLPreprocessor will copy pattern imports in usual way.")

            elif self.read_test and self.recursive_imports and not self.usual_imports:
                log.debug("Recursive imports with test patterns used - I will find and copy any imports I found in "
                          "TKN_CORE including patterns from test.py")

            elif self.read_test and not self.recursive_imports and not self.usual_imports:
                log.debug("No imports will be run but test.py will be parsed to use it's arguments in further process.")

            else:
                log.info("Import arguments not set or don't know what scenario to use it this case: "+str(self.operational_args))
        else:
            log.info("Import arguments not set or don't know what scenario to use it this case: "+str(self.operational_args))
            log.debug("Import arguments are set to False.")
            self.recursive_imports = False
            self.usual_imports     = False
            self.read_test         = False

    def check_args_set(self, **args_from_cmd):
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

        return parse_args.gather_args(known_args=args_from_cmd['known_args'],
                                      extra_args=args_from_cmd['extra_args'])

    def cond_args(self, **conditional_args_set):
        """
        This section will compose sets of functions to execute.
        Each function will use conditional arguments to understand which scenario to use now.
        To understand each scenario - read the correspond function with suffix 'cond'.

        This is some logic explanation, but not the active scheme to implement:
            Examples:
            Development:
                For upload:
                    Dev VM:
                        workspace, tplpre, no imports, preproc, syntax_check, addm_dev, ssh
                        workspace, tplpre, recursive imports, preproc, syntax_check, addm_dev, ssh
                        workspace, tplpre, test + recursive imports, preproc, syntax_check, addm_dev, ssh
                        workspace, -
                            if addm_dev workspace did not match - upload to hardcoded dev.
                    Not dev vm:
                        workspace, tplpre, no imports, preproc, syntax_check, addm_dev, ssh
                        workspace, tplpre, recursive imports, preproc, syntax_check, addm_dev, ssh
                        workspace, tplpre, test + recursive imports, preproc, syntax_check, addm_dev, ssh
                        workspace, -
                            if addm_dev workspace did not match - upload to hardcoded dev.

                For local only:
                    workspace, tplpre, no imports, preproc, syntax_check
                    workspace, tplpre, recursive imports, preproc, syntax_check
                    workspace, tplpre, test + recursive imports, preproc, syntax_check

                Out of workspace:
                    p4_workspace, tpl, ssh
                    p4_workspace, tpl, No ssh

            Customer:
                tku_workspace, tpl, no imports, ssh
                tku_workspace, tpl, recursive imports, ssh

        :return:
        """
        log = self.logging

        # TODO: Add check for empty dict:
        addm_conditions = conditional_args_set['addm_args_set']
        local_conditions = conditional_args_set['full_path_args']
        operational_conditions = conditional_args_set['operational_args']

        # This will be re-write if success:
        imports_f = False
        preproc_f = False
        syntax_check_f = False
        zip_files_f = False
        addm_activate_f = False
        upload_f = False
        scan_f = False

        addm_zip = ''
        local_zip = ''

        # TODO: Debug disable:
        operational_conditions_debug = {'recursive_imports': False,
                                        'usual_imports': False,
                                        'read_test': False}

        addm_conditions_debug = {
                                 'scan_hosts': '172.25.144.95, 172.25.144.39',
                                 # 'scan_hosts': '',
                                 'addm_prod': 'Bobblehat',
                                 'disco_mode': 'record',
                                 # 'disco_mode': '',
                                 'addm_ver': '11.1',
                                 'ssh_connection': False,
                                 # 'ssh_connection': addm_conditions['ssh_connection'],
                                 'tpl_folder': 'tpl113',
                                 'dev_vm_check': True,
                                 'dev_vm_path': '/usr/tideway/TKU',
                                 'tpl_vers': '1.13'
                                }

        # addm_conditions = addm_conditions_debug
        # operational_conditions = operational_conditions_debug

        # Addm args for scan
        if addm_conditions['scan_hosts'] \
                and addm_conditions['disco_mode'] \
                and addm_conditions['ssh_connection']:

            log.info("ADDM Scan args are present, current files will be uploaded to ADDM and Scan will be started.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_conditions=operational_conditions,
                                              tpl_version=addm_conditions['addm_ver'])

            # Genarate addm working dir based on DEV condition:
            addm_working_dir = self.addm_dev_cond(addm_conditions['dev_vm_check'])

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            zip_files_f, \
            addm_zip, \
            local_zip = self.pattern_path_cond(addm_conditions['dev_vm_check'],
                                               operational_conditions,
                                               addm_working_dir)

            # Using path to zip result from above - activate it in ADDM
            upload_f, \
            addm_activate_f = self.zip_activ_cond(addm_vm_condition=addm_conditions['dev_vm_check'],
                                                  addm_zip=addm_zip,
                                                  local_zip=local_zip,
                                                  module_name=self.full_path_args['pattern_folder'])

            # Start scan action:
            scan_f = self.make_scan(disco_mode=addm_conditions['disco_mode'],
                                    host_list=addm_conditions['scan_hosts'],
                                    module_name=self.full_path_args['pattern_folder']
                                    )

        # When I have no args for scan AND NO args for ADDM disco, but have arg for tpl_vers - proceed files locally with that version.
        elif not addm_conditions['disco_mode'] \
                and not addm_conditions['scan_hosts'] \
                and addm_conditions['tpl_folder'] \
                and addm_conditions['ssh_connection']:

            log.info("No ADDM Scan and discovery args are present. Local processing with tpl version gathered from live ADDM.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_conditions=operational_conditions,
                                              tpl_version=addm_conditions['addm_ver'])

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            addm_working_dir = 'Null'
            zip_files_f, \
            addm_zip, \
            local_zip = self.pattern_path_cond(addm_vm_condition=None,
                                               operational_conditions=operational_conditions,
                                               addm_working_dir=addm_working_dir)

            log.info("Patterns zipped with tpl_ver from ADDM: "+str(addm_conditions['tpl_folder'])+" path to zip: "+str(local_zip))

        # When I have NO args for Scan, but have args for ADDM status and disco - will start upload only.
        elif not addm_conditions['scan_hosts'] \
                and addm_conditions['tpl_folder'] \
                and addm_conditions['disco_mode'] \
                and addm_conditions['ssh_connection']:

            log.info("ADDM Upload args are present, current files will be uploaded to ADDM. No scan.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_conditions=operational_conditions,
                                              tpl_version=addm_conditions['addm_ver'])

            # Genarate addm working dir based on DEV condition:
            addm_working_dir = self.addm_dev_cond(addm_conditions['dev_vm_check'])

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            zip_files_f, \
            addm_zip, \
            local_zip = self.pattern_path_cond(addm_conditions['dev_vm_check'],
                                               operational_conditions,
                                               addm_working_dir)


            # Using path to zip result from above - activate it in ADDM
            upload_f, \
            addm_activate_f = self.zip_activ_cond(addm_vm_condition=addm_conditions['dev_vm_check'],
                                                  addm_zip=addm_zip,
                                                  local_zip=local_zip,
                                                  module_name=self.full_path_args['pattern_folder'])

            # No Scan action because: not addm_conditions['scan_hosts'] just upload and activate.

        # No addm args:
        elif not addm_conditions['ssh_connection']:
            # I have no active connection to ADDM so I don't know about tpl version to geregate and zip
            #  - SO I will just import, prepcor and check syntax
            log.info("No ADDM connections args are present. Local processing.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions)

            # Run syntax check based on cond args:
            # Maybe I can add tpl_version for offline checks but what for?
            syntax_check_f = self.syntax_cond(operational_conditions=operational_conditions,
                                              tpl_version='')

            addm_zip = 'There is no ADDM connection, programm is running in local mode.'
            local_zip = 'There is no ADDM connection, programm is running in local mode.'
            addm_working_dir = 'There is no ADDM connection, programm is running in local mode.'

        # I don't know:
        else:
            log.info("This set of conditional arguments is not supported with my logic, Please read docs.")

        conditional_functions = {
            'imports_f': imports_f,
            'preproc_f': preproc_f,
            'syntax_check_f': syntax_check_f,
            'zip_files_f': zip_files_f,
            'upload_f': upload_f,
            'addm_activate_f': addm_activate_f,
            'scan_f': scan_f,
        }

        conditional_results = {
            'addm_zip': addm_zip,
            'local_zip': local_zip,
            'addm_working_dir': addm_working_dir,
        }

        return conditional_functions, conditional_results

    def make_function_set(self):
        """

        :return: pair of function sets with conditional functions to execute and result to debug.
        """
        log = self.logging

        conditional_functions, \
        conditional_results = self.cond_args(full_path_args = self.full_path_args,
                                             addm_args_set = self.addm_args_set,
                                             operational_args = self.operational_args)

        return conditional_functions, conditional_results

    def imports_cond(self, operational_conditions):
        """
        Based on condition argumets use different scenarios of importing patterns:
        usual_imports - When you don't want to import whole set of modules but only ones are used in current pattern.
            Preprocessor will import.

        recursive_imports - When you want to import modules for each pattern in working dir and each it recursive.
            I will import in my own way for active pattern + all imports and included.

        test + recursive_imports - As recursive imports but also includes patterns from self.setupPatterns from test.py
            I will import anything from active pattern + all I found in test.py and included.


        :param local_conditions:
        :param operational_conditions:
        :return:
        """
        log = self.logging


        # NORMAL IMPORTS
        if operational_conditions['usual_imports']:
            log.debug("No extra imports will be run. Tplpreprocessor will import as is.")

            import_cond_dict = {
                                'parse_tests_patterns':  False,
                                'parse_tests_queries':   False,
                                'import_patterns':       False
                               }

        # RECURSIVE MODE:
        elif operational_conditions['recursive_imports'] and not operational_conditions['read_test']:
            log.debug("Run recursive imports mode.")

            # Import tplpre's in recursive mode:
            imports_f = self.make_imports(extra_patterns=None)

            import_cond_dict = {
                                'parse_tests_patterns': False,
                                'parse_tests_queries': False,
                                'import_patterns': imports_f
                               }

        # TESTs + RECURSIVE MODE:
        elif operational_conditions['read_test'] and operational_conditions['recursive_imports']:
            log.debug("Run test+recursive imports mode.")

            # Read test.py and extract query for future validation after addm scan and save model:
            # Later if -T in arg - use this, if no - just ignore.
            query_t = self.make_test_read_query()

            # Read test.py and extract list of patterns from self.setupPatterns
            # This is list of patterns I need to import from test.py.
            imports_t = TestRead(log).import_pattern_tests(self.working_dir, self.tku_patterns_t)

            # Import tplpre's in recursive mode with extras from test.py:
            imports_f = self.make_imports(imports_t)

            import_cond_dict = {
                                'parse_tests_queries': query_t,
                                'parse_tests_patterns': False,
                                'import_patterns': imports_f
                               }

        # SOLO MODE:
        elif not operational_conditions['read_test'] and not operational_conditions['recursive_imports'] and not operational_conditions['usual_imports']:
            log.info("There are no dev arguments found for Test read, or imports, or recursive imports. "
                     "Using as standalone tplpre.")

            import_cond_dict = {
                                'parse_tests_patterns': False,
                                'parse_tests_queries': False,
                                'import_patterns': False
                               }

        return import_cond_dict

    def preproc_cond(self, operational_conditions):
        """
        Based on conditional args - run Preproc with import folder
        after my own method, or usual preproc method or even solo pattern preproc.

        :param operational_conditions: What type of imports dict
        :return:
        """
        log = self.logging

        # Preproc on NORMAL IMPORTS
        if operational_conditions['usual_imports'] and not operational_conditions['recursive_imports'] and not operational_conditions['read_test']:
            log.info("TPLPreprocessor will run on active file and import by its own logic.")
            preproc_f = self.make_preproc(workspace=self.workspace,
                                          input_path=self.full_path,
                                          output_path=self.working_dir,
                                          mode="usual_imports")

        # Preproc will run on all files from folder 'imports'
        elif operational_conditions['recursive_imports'] or operational_conditions['read_test'] and not operational_conditions['usual_imports']:
            log.info("TPLPreprocessor will run on imports folder after my importing logic.")
            # After R imports are finish its work - run TPLPreprocessor on it
            preproc_f = self.make_preproc(workspace=self.workspace,
                                          input_path=self.working_dir+os.sep+"imports",
                                          output_path=self.working_dir+os.sep+"imports",
                                          mode="recursive_imports")

        # SOLO MODE:
        elif not operational_conditions['read_test'] and not operational_conditions['recursive_imports'] and not operational_conditions['usual_imports']:
            log.info("TPLPreprocessor will run on active file without any additional imports.")

            preproc_f = self.make_preproc(workspace=self.workspace,
                                          input_path=self.full_path,
                                          output_path=self.working_dir,
                                          mode="solo_mode")

        return preproc_f

    def syntax_cond(self, operational_conditions, tpl_version):
        """
        Run syntax with options based on conditional arguments.

        If ADDM did not return any version - syntax check will run for all available versions.
        Optional: arg set of tpl version can be used here.
        :return:
        """
        log = self.logging

        # Preproc on NORMAL IMPORTS
        if operational_conditions['usual_imports']:
            log.info("Syntax check will run on tpl folders after usual TPLPreproc output.")

            # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
            syntax_check_f = self.make_syntax_check(self.working_dir,
                                                    disco_ver=tpl_version)

        # Preproc will run on all files from folder 'imports'
        elif operational_conditions['recursive_imports'] or operational_conditions['read_test']:
            log.info("Syntax check will run on imports folder after my importing logic.")

            # After TPLPreprocessor finished its work - run Syntax Check on folder imports
            # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
            syntax_check_f = self.make_syntax_check(self.working_dir+os.sep+"imports",
                                                    disco_ver=tpl_version)

        # SOLO MODE:
        elif not operational_conditions['read_test'] and not operational_conditions['recursive_imports'] and not operational_conditions['usual_imports']:
            log.info("1/1 Syntax check will run on active file without any additional imports.")
            log.debug("1/2 This means that all imports was already created and you just want to check syntax for active pattern.")

            # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
            # In this condition syntax check will hope that imports are already in folder after previous runs.
            syntax_check_f = self.make_syntax_check(self.working_dir,
                                                    disco_ver=tpl_version)


        return syntax_check_f

    def addm_dev_cond(self, addm_vm_condition):
        """
        Based on args - make decision is ADDM dev or not - and compose paths for DEV or not.

        :return: paths
        """
        log = self.logging

        if addm_vm_condition:
            log.info("DEV ADDM is working - files will be activated in mirrored filesystem.")

            # Compose paths:
            local_logic = LocalLogic(log)
            addm_working_dir = local_logic.addm_compose_paths(dev_vm_path=self.dev_vm_path,
                                                              pattern_folder=self.full_path_args['pattern_folder'])

        elif not addm_vm_condition:
            log.info("Usual ADDM is working - files will be uploaded to '/usr/tideway/TKU/Tpl_DEV/' folder and activated.")
            addm_working_dir = '/usr/tideway/TKU/Tpl_DEV'

        return addm_working_dir

    def pattern_path_cond(self, addm_vm_condition, operational_conditions, addm_working_dir):
        """
        Based on operational conditions - decide which path to use for patterns zip and upload\activate

        This functions should be called with argument (result) from addm_dev_cond()
            which is path to remote result folder where zip patterns activate or where to download if dev_vm is False.

        Possible paths based on args:

            if solo_mode:
                - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.tpl
                - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
            if usual_imports or recursive_imports:
                - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.tpl
                - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

            if dev_vm:
                local          - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                               - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

                remote(mirror) - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/tpl<version>/PatternName.zip
                               - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/imports/tpl<version>/PatternName.zip
            if not dev_vm:
                local          - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                               - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

                remote(not DEV) - /usr/tideway/TKU/Tpl_DEV/PatternName.zip

        addm_zip_f - closure functions of zipping patterns
        addm_zip - path to zip in addm FS if available
        local_zip - path to zip in local FS


        :return: addm_zip_f, addm_zip, local_zip
        """
        log = self.logging

        if operational_conditions['usual_imports'] or operational_conditions['recursive_imports']:
            log.debug("Making zip from imported patterns.")

            # Include 'imports' dir into the path:
            imports_dir = os.sep+"imports"+os.sep
            # Path of acive pattern folder + imports dir + tpl<version dir>:
            # 'working_dir': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem',
            # path_to_result: d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\imports\tpl113\
            path_to_result = self.full_path_args['working_dir']+imports_dir+self.tpl_folder+os.sep

            # Pattern remote path in ADDM FS:
            if addm_vm_condition:
                # On DEV ADDM (example docs: remote(mirror)): /usr/tideway/TKU/addm/tkn_main/tku_patterns/...
                addm_result_folder = addm_working_dir+"/imports/"+self.tpl_folder
                # I do not need this, because on DEV VM I will just activate zip in mirror FS
                local_zip = 'ADDM is in DEV mode - not need to point to local zip file.'
            elif not addm_vm_condition:
                # Not on DEV ADDM (example docs: remote(not DEV)): /usr/tideway/TKU/Tpl_DEV/
                # addm_result_folder: /usr/tideway/TKU/Tpl_DEV
                addm_result_folder = addm_working_dir
                # local_zip: d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\imports\tpl113\BMCRemedyARSystem.zip
                local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                log.debug("local_zip: "+str(local_zip))
            else:
                # I don not use this, because I want ti zip files without uploading:
                addm_result_folder = addm_working_dir
                # Just make zip on local files and don't move it:
                local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                log.debug("local_zip: "+str(local_zip))

            # Making function obj for ZIP
            zip_mirror = addm_result_folder+"/"+self.full_path_args['pattern_folder'] + '.zip'
            addm_zip_f = self.make_zip(path_to_result=path_to_result,
                                       active_folder=self.full_path_args['pattern_folder'])

            # Path to zip with import included:
            # path_to_zip: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/BMCRemedyARSystem/imports/tpl113/BMCRemedyARSystem.zip
            addm_zip = zip_mirror

            log.debug("addm_zip: "+str(addm_zip))
            log.debug("addm_result_folder: "+str(addm_result_folder))
            log.debug("path_to_result: "+str(path_to_result))

        elif not operational_conditions['usual_imports'] and not operational_conditions['recursive_imports']:
            log.debug("Imports condition - NOT DEV IMPORTS to addm: Making zip with one active file.")

            # Path of active pattern to ZIP:
            # 'working_dir': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem',
            # path_to_result: d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\tpl113\
            path_to_result = self.full_path_args['working_dir']+os.sep+self.tpl_folder+os.sep

            # Pattern remote path in ADDM FS:
            # addm_zip_path = addm_working_dir+"/"+self.tpl_folder+"/"+self.full_path_args['file_name']+".tpl"

            # Pattern remote path in ADDM FS:
            if addm_vm_condition:
                # On DEV ADDM (example docs: remote(mirror)):
                # addm_result_folder: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/BMCRemedyARSystem/tpl113
                addm_result_folder = addm_working_dir+"/"+self.tpl_folder
                # I do not need this, because on DEV VM I will just activate zip in mirror FS
                local_zip = 'ADDM is in DEV mode - not need to point to local zip file.'
            elif not addm_vm_condition:
                # Not on DEV ADDM (example docs: remote(not DEV)): /usr/tideway/TKU/Tpl_DEV/
                # addm_result_folder: /usr/tideway/TKU/Tpl_DEV
                addm_result_folder = addm_working_dir
                # local_zip: d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\tpl113\BMCRemedyARSystem.zip
                local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                log.debug("local_zip: "+str(local_zip))
            else:
                # I don not use this, because I want ti zip files without uploading:
                addm_result_folder = addm_working_dir
                # Just make zip on local files and don't move it:
                local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                log.debug("local_zip: "+str(local_zip))

            # Making function obj for ZIP
            zip_remote = addm_result_folder+"/"+self.full_path_args['pattern_folder'] + '.zip'
            addm_zip_f = self.make_zip(path_to_result=path_to_result,
                                       active_folder=self.full_path_args['pattern_folder'])

            # Path to zip with single pattern included:
            # addm_zip: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/BMCRemedyARSystem/tpl113/BMCRemedyARSystem.zip
            addm_zip = zip_remote

            log.debug("addm_zip: "+str(addm_zip))
            log.debug("addm_result_folder: "+str(addm_result_folder))
            log.debug("path_to_result: "+str(path_to_result))

        return addm_zip_f, addm_zip, local_zip

    def zip_activ_cond(self, addm_vm_condition, addm_zip, local_zip, module_name):
        """
        Based on ADDM state - if DEV_VM or not - choose folder where activate or upload and activate ZIP with patterns.

        if dev_vm:
            local          - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                           - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

            remote(mirror) - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/tpl<version>/PatternName.zip
                           - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/imports/tpl<version>/PatternName.zip
        if not dev_vm:
            local          - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                           - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

            remote         - /usr/tideway/TKU/Tpl_DEV/PatternName.zip

        upload_f - closure function with zip upload to ADDM
        addm_activate_f - closure function with pattern activation in ADDM (False if upload only mode)

        :param addm_vm_condition: if dev_vm
        :param addm_zip: path to zip in ADDM FS
        :param local_zip: path to zip in local FS
        :param module_name: usually is the name of pattern folder
        :return: upload_f, addm_activate_f
        """
        log = self.logging

        if addm_vm_condition:
            # Just activate zip in mirrored path:
            log.info("Files will be activated in mirrored filesystem.")
            addm_activate_f = self.make_activate_zip(zip_path=addm_zip,
                                                     module_name=module_name)
            upload_f = False

        elif not addm_vm_condition:
            # Upload zip to addm custom folder and then activate:
            log.info("Files will be uploaded to '/usr/tideway/TKU/Tpl_DEV/' folder and then activated.")

            # UPLOAD zip to ADDM via SFTP:
            upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)

            addm_activate_f = self.make_activate_zip(zip_path=addm_zip,
                                                     module_name=module_name)

        return upload_f, addm_activate_f

    def make_test_read_query(self):
        """
        Closure for reading test.py queries.
        :return: func with query results list.
        """
        log = self.logging

        def test_queries():
            test_read = TestRead(log)
            test_read.query_pattern_tests(self.working_dir)

        return test_queries

    def make_imports(self, extra_patterns):
        """
        Closure for imports function.
        Based or arguments - decide which import will run.
        Or nothing to run at all.

        :return: func with imports
        """
        log = self.logging

        def importer():
            tpl_imports = TPLimports(log, self.full_path_args)
            # Now I don't need args because class was initialized with args above:
            tpl_imports.import_modules(extra_patterns)
        return importer

    def make_preproc(self, workspace, input_path, output_path, mode):
        """
        Closure for preproc function.

        :param mode: str operational mode
        :param output_path: str - where to output files.
        :param input_path: str - what file or folder to preproc.
        :param workspace: str - path to p4 workspace.

        :return: func preproc with args in it
        """
        log = self.logging

        def pre_processing():
            preproc = Preproc(log)
            preproc.tpl_preprocessor(workspace, input_path, output_path, mode)
        return pre_processing

    def make_syntax_check(self, working_dir, disco_ver):
        """
        Closure for syntax check function.

        Run LOCAL syntax check procedure in selected folders or files.
        Can run ONLY when imports from patter are also in the same folder.
        Should be ignored in SOLO MODE.

        :param working_dir: str - input dir where run syntax check
        :param disco_ver: str - version of discover engine to use for check, if empty - run all.
        :return: func - syntax check with args in it.
        """
        log = self.logging

        def syntax_check():
            syntax = SyntaxCheck(log)
            if_check = syntax.syntax_check(working_dir, disco_ver)
            return if_check

        return syntax_check

    def make_zip(self, path_to_result, active_folder):
        """
        Closure for zipper function.
        Make zip for local folder!
        :type active_folder: str - folder where pattern lies and ready to zip
        :type path_to_result: str - path to zip with patterns
        :return: func zipper
        """
        log = self.logging

        def zipper():
            local_logic = LocalLogic(log)
            # Zip local processed files and return path to zip on local and name if zip for addm mirror FS:
            local_logic.make_zip(path_to_result, active_folder)

        return zipper

    def make_upload_remote(self, zip_on_local, zip_on_remote):
        """
        Closure for pattern upload on remote addm via SFTP.
        :type zip_on_remote: str possible path to remote zip file
        :type zip_on_local: str actual path to local zip file
        :return: activate patterns func
        """
        log = self.logging

        def activate():
            addm = AddmOperations(log, self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm.upload_knowledge(zip_on_local=zip_on_local, zip_on_remote=zip_on_remote)

        return activate
    
    def make_activate_zip(self, zip_path, module_name):
        """
        Closure for pattern activation.
        Input arg to zip path - can be local or remote.

        :type module_name: str - usually name of pattern folder
        :type zip_path: str - actual path to mirrored or uploaded zip
        :return: func activate patterns
        """
        log = self.logging

        def activate():
            addm = AddmOperations(log, self.ssh)
            # Activate zip package using path from arg (local|remote):
            addm.activate_knowledge(zip_path, module_name)

        return activate
    
    def make_scan(self, disco_mode, host_list, module_name):
        """
        Closure for addm start scan function with args.
        :type module_name: str - usually name of pattern folder.
        :type host_list: str - list of hosts to scan, from known_args.
        :type disco_mode: str - discovery mode, from known_args.
        :return: func start scan with args
        """
        log = self.logging

        def scan():
            addm_scan = AddmScan(log, self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm_scan.addm_scan(disco_mode, host_list, self.full_path_args['pattern_folder'])

        return scan