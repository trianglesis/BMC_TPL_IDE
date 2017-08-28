"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
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
        '''
        Initialize with options for logica loperations.
        Check arg sets and output messages for different option scenarios.

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

        :param kwargs:
        '''

        logging = kwargs['logging']
        self.logging = logging
        log = self.logging

        # Get all available arguments in three sets based on its type:
        self.full_path_args, \
        self.operational_args, \
        self.addm_args_set = self.check_args_set(known_args = kwargs['known_args'],
                                                 extra_args = kwargs['extra_args'])

        # DEBUG
        # import json
        # from pprint import pformat
        # print(json.dumps(self.addm_args_set, indent=4, ensure_ascii=False, default=pformat))

        # Check args in init module to furter assign on function bodies:
        if self.full_path_args:
            '''
                Examples of arg sets
        
                    PATH ARGS: {
                        "BLADE_ENCLOSURE_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+",
                        "SYSTEM_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-System-2017-07-1-ADDM-11.1+",
                        "tkn_main_t": "",
                        "tku_patterns_t": "",
                        "MIDDLEWAREDETAILS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+",
                        "workspace": "D:\\TKU",
                        "file_name": "PatternName",
                        "CLOUD_t": "",
                        "full_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+\\PatternName.tpl",
                        "DBDETAILS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+",
                        "working_dir": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+",
                        "CORE_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+",
                        "file_ext": "tpl",
                        "pattern_folder": "TKU-Core-2017-07-1-ADDM-11.1+",
                        "MANAGEMENT_CONTROLLERS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+",
                        "STORAGE_t": "",
                        "buildscripts_t": "",
                        "environment_condition": "customer_tku",
                        "LOAD_BALANCER_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-LoadBalancer-2017-07-1-ADDM-11.1+",
                        "tkn_sandbox_t": ""
                    }
        
                    PATH ARGS: {
                        "STORAGE_t": "d:\\addm\\tkn_main\\tku_patterns\\STORAGE",
                        "CORE_t": "d:\\addm\\tkn_main\\tku_patterns\\CORE",
                        "buildscripts_t": "d:\\addm\\tkn_main\\buildscripts",
                        "SYSTEM_t": "d:\\addm\\tkn_main\\tku_patterns\\SYSTEM",
                        "tkn_sandbox_t": "d:\\addm\\tkn_sandbox",
                        "file_name": "PatternName",
                        "DBDETAILS_t": "d:\\addm\\tkn_main\\tku_patterns\\DBDETAILS",
                        "tkn_main_t": "d:\\addm\\tkn_main",
                        "environment_condition": "developer_tplpre",
                        "BLADE_ENCLOSURE_t": "d:\\addm\\tkn_main\\tku_patterns\\BLADE_ENCLOSURE",
                        "working_dir": "d:\\addm\\tkn_main\\tku_patterns\\CORE\\PatternName",
                        "MIDDLEWAREDETAILS_t": "d:\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS",
                        "MANAGEMENT_CONTROLLERS_t": "d:\\addm\\tkn_main\\tku_patterns\\MANAGEMENT_CONTROLLERS",
                        "LOAD_BALANCER_t": "d:\\addm\\tkn_main\\tku_patterns\\LOAD_BALANCER",
                        "full_path": "d:\\addm\\tkn_main\\tku_patterns\\CORE\\PatternName\\PatternName.tplpre",
                        "CLOUD_t": "d:\\addm\\tkn_main\\tku_patterns\\CLOUD",
                        "file_ext": "tplpre",
                        "workspace": "d:",
                        "pattern_folder": "PatternName",
                        "tku_patterns_t": "d:\\addm\\tkn_main\\tku_patterns"
                    }

            '''

            self.tku_patterns_t = self.full_path_args['tku_patterns_t']
            self.workspace      = self.full_path_args['workspace']
            self.full_path      = self.full_path_args['full_path']
            self.working_dir    = self.full_path_args['working_dir']

            if not self.working_dir:
                log.error("File working dir is not extracted - I cannot proceed any function.")

            log.debug("Full path arguments are set. It will be used to choose programm working scenario.")
        else:
            log.debug("No full path arguments are set. I can do nothing with this.")

        if self.addm_args_set:
            '''
            ADDM VM ARGS: {dev_vm_path": "/usr/tideway/TKU",
                           "dev_vm_check": true,
                           "tpl_folder": "tpl113",
                           "tpl_vers": "1.13",
                           "addm_prod": "Bobblehat",
                           "scan_hosts": "172.25.144.95, 172.25.144.39",
                           "addm_ver": "11.1",
                           "system_password": "system",
                           "system_user": "system",
                           "ssh_connection": "<paramiko.client.SSHClient object at 0x00000000035C6668>",
                           "disco_mode": "record"}
            '''
            self.ssh            = self.addm_args_set['ssh_connection']
            self.tpl_folder     = self.addm_args_set['tpl_folder']
            self.dev_vm_path    = self.addm_args_set['dev_vm_path']

            log.debug("ADDM arguments are gathered from addm host. "
                      "It will be used to choose programm working scenario.")
        else:
            log.debug("ADDM arguments are gathered or wasn't set. Programm will work on local mode.")

        if self.operational_args:
            '''
                {
                    "read_test": false,
                    "usual_imports": true,
                    "recursive_imports": false
                }

            '''

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

        # Set examples in __init__ docstrings:
        addm_conditions        = conditional_args_set['addm_args_set']
        local_conditions       = conditional_args_set['full_path_args']
        operational_conditions = conditional_args_set['operational_args']


        # Set operational option for dev or customer:
        environment_condition = local_conditions['environment_condition']
        log.info("Programm's global logic module operating in: '"+str(environment_condition)+"' mode.")

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
        operational_conditions_debug = dict(recursive_imports=False,
                                            usual_imports=False,
                                            read_test=False)

        addm_conditions_debug = dict(
                                     scan_hosts='172.25.144.95, 172.25.144.39',
                                     addm_prod='Bobblehat',
                                     disco_mode='record',
                                     addm_ver='11.1',
                                     # ssh_connection=False,
                                     ssh_connection=addm_conditions['ssh_connection'],
                                     tpl_folder='tpl113',
                                     dev_vm_check=True,
                                     dev_vm_path='/usr/tideway/TKU',
                                     tpl_vers='1.13'
                                    )

        # addm_conditions = addm_conditions_debug
        # operational_conditions = operational_conditions_debug

        # Addm args for scan
        if addm_conditions['scan_hosts'] \
                and addm_conditions['disco_mode'] \
                and addm_conditions['ssh_connection']:

            log.info("ADDM Scan args are present, current files will be uploaded to ADDM and Scan will be started.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_conditions = operational_conditions,
                                              tpl_version            = addm_conditions['addm_ver'],
                                              local_conditions       = local_conditions)

            # Genarate addm working dir based on DEV condition:
            addm_working_dir = self.addm_dev_cond(addm_conditions['dev_vm_check'],
                                                  environment_condition)

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            zip_files_f, \
            addm_zip, \
            local_zip = self.pattern_path_cond(addm_conditions        = addm_conditions,
                                               operational_conditions = operational_conditions,
                                               addm_working_dir       = addm_working_dir,
                                               local_conditions       = local_conditions)

            # Using path to zip result from above - activate it in ADDM
            upload_f, \
            addm_activate_f = self.zip_activ_cond(addm_conditions  = addm_conditions,
                                                  addm_zip         = addm_zip,
                                                  local_zip        = local_zip,
                                                  local_conditions = local_conditions)

            # Start scan action:
            # Better to use filename as active file - which initiates this run:
            scan_f = self.make_scan(addm_conditions = addm_conditions,
                                    module_name     = self.full_path_args['file_name'])

        # When I have no args for scan AND NO args for ADDM disco, but have arg for tpl_vers - proceed files locally with that version.
        elif not addm_conditions['disco_mode'] \
                and not addm_conditions['scan_hosts'] \
                and addm_conditions['tpl_folder'] \
                and addm_conditions['ssh_connection']:

            log.info("No ADDM Scan and discovery args are present. Local processing with tpl version gathered from live ADDM.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_conditions = operational_conditions,
                                              tpl_version            = addm_conditions['addm_ver'])

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            addm_working_dir = 'Null'
            zip_files_f, \
            addm_zip, \
            local_zip = self.pattern_path_cond(addm_vm_condition      = None,
                                               operational_conditions = operational_conditions,
                                               addm_working_dir       = addm_working_dir,
                                               local_conditions       = local_conditions)

            log.info("Patterns zipped with tpl_ver from ADDM: "+str(addm_conditions['tpl_folder'])+" path to zip: "+str(local_zip))

        # When I have NO args for Scan, but have args for ADDM status and disco - will start upload only.
        elif not addm_conditions['scan_hosts'] \
                and addm_conditions['tpl_folder'] \
                and addm_conditions['disco_mode'] \
                and addm_conditions['ssh_connection']:

            log.info("ADDM Upload args are present, current files will be uploaded to ADDM. No scan.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_conditions = operational_conditions,
                                              tpl_version            = addm_conditions['addm_ver'],
                                              local_conditions       = local_conditions)

            # Genarate addm working dir based on DEV condition:
            addm_working_dir = self.addm_dev_cond(addm_conditions['dev_vm_check'], environment_condition)

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            zip_files_f, \
            addm_zip, \
            local_zip = self.pattern_path_cond(addm_conditions        = addm_conditions,
                                               operational_conditions = operational_conditions,
                                               addm_working_dir       = addm_working_dir,
                                               local_conditions       = local_conditions)


            # Using path to zip result from above - activate it in ADDM
            upload_f, \
            addm_activate_f = self.zip_activ_cond(addm_conditions = addm_conditions,
                                                  addm_zip        = addm_zip,
                                                  local_zip       = local_zip,
                                                  local_conditions = local_conditions)

            # No Scan action because: not addm_conditions['scan_hosts'] just upload and activate.

        # No addm args:
        elif not addm_conditions['ssh_connection']:
            # I have no active connection to ADDM so I don't know about tpl version to geregate and zip
            #  - SO I will just import, prepcor and check syntax
            log.info("No ADDM connections args are present. Local processing.")

            # Import patterns if needed on mode set in operational_conditions
            imports_f = self.imports_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(operational_conditions = operational_conditions,
                                          local_conditions       = local_conditions)

            # Run syntax check based on cond args:
            # Maybe I can add tpl_version for offline checks but what for?
            syntax_check_f = self.syntax_cond(operational_conditions = operational_conditions,
                                              tpl_version            = '',
                                              local_conditions       = local_conditions)

            addm_zip         = 'There is no ADDM connection, programm is running in local mode.'
            local_zip        = 'There is no ADDM connection, programm is running in local mode.'
            addm_working_dir = 'There is no ADDM connection, programm is running in local mode.'

        # I don't know:
        else:
            log.info("This set of conditional arguments is not supported with my logic, Please read docs.")

        conditional_functions = dict(imports_f       = imports_f,
                                     preproc_f       = preproc_f,
                                     syntax_check_f  = syntax_check_f,
                                     zip_files_f     = zip_files_f,
                                     upload_f        = upload_f,
                                     addm_activate_f = addm_activate_f,
                                     scan_f          = scan_f)

        conditional_results = dict(addm_zip         = addm_zip,
                                   local_zip        = local_zip,
                                   addm_working_dir = addm_working_dir)

        return conditional_functions, conditional_results

    def make_function_set(self):
        """
        Output:
            conditional_functions =
            {
            "zip_files_f": "<function GlobalLogic.make_zip.<locals>.zipper at 0x000000000396E048>",
            "scan_f": "<function GlobalLogic.make_scan.<locals>.scan at 0x000000000396E0D0>",
            "preproc_f": "<function GlobalLogic.make_preproc.<locals>.pre_processing at 0x000000000395FEA0>",
            "imports_f": {
                "parse_tests_patterns": false,
                "parse_tests_queries": false,
                "import_patterns": "<function GlobalLogic.make_imports.<locals>.importer at 0x00000000036662F0>"
            },
            "addm_activate_f": "<function GlobalLogic.make_activate_zip.<locals>.activate at 0x000000000395FF28>",
            "syntax_check_f": "<function GlobalLogic.make_syntax_check.<locals>.syntax_check at 0x000000000395FBF8>",
            "upload_f": false
            }

            conditional_results =
            {
                "addm_zip": "/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName/imports/tpl113/PatternName.zip",
                "addm_working_dir": "/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName",
                "local_zip": "ADDM is in DEV mode - not need to point to local zip file."
            }

        :return: pair of function sets with conditional functions to execute and result to debug.
        """
        log = self.logging

        conditional_functions, conditional_results = self.cond_args(full_path_args   = self.full_path_args,
                                                                    addm_args_set    = self.addm_args_set,
                                                                    operational_args = self.operational_args)

        return conditional_functions, conditional_results

    def imports_cond(self, **logical_conditions):
        """
        Based on condition argumets use different scenarios of importing patterns:

        Including customer condtition it now will decide how to import patterns.

        usual_imports - When you don't want to import whole set of modules but only ones are used in current pattern.
            Preprocessor will import.

        recursive_imports - When you want to import modules for each pattern in working dir and each it recursive.
            I will import in my own way for active pattern + all imports and included.

        test + recursive_imports - As recursive imports but also includes patterns from self.setupPatterns from test.py
            I will import anything from active pattern + all I found in test.py and included.

        Output:
        {
            "parse_tests_queries": false,
            "import_patterns": "<function GlobalLogic.make_imports.<locals>.importer at 0x00000000036667B8>",
            "parse_tests_patterns": false
        }

        :param environment_condition: mode to operate with - dev or customer.
        :param operational_conditions:
        :return:
        """
        log = self.logging

        # Set examples in __init__ docstrings:
        operational_conditions = logical_conditions['operational_conditions']
        environment_condition  = logical_conditions['local_conditions']['environment_condition']
        local_conditions       = logical_conditions['local_conditions']

        import_cond_dict = dict(parse_tests_patterns=False,
                                parse_tests_queries=False,
                                import_patterns=False)

        if environment_condition == 'developer_tplpre':
            # NORMAL IMPORTS
            if operational_conditions['usual_imports']:
                log.debug("No extra imports will be run. Tplpreprocessor will import as is.")

                import_cond_dict = dict(parse_tests_patterns=False,
                                        parse_tests_queries=False,
                                        import_patterns=False)

                return import_cond_dict

            # RECURSIVE MODE:
            elif operational_conditions['recursive_imports'] and \
                    not operational_conditions['read_test']:
                log.debug("Run recursive imports mode.")

                # Import tplpre's in recursive mode:
                imports_f = self.make_imports(local_conditions = local_conditions,
                                              extra_patterns   = None)

                import_cond_dict = dict(parse_tests_patterns = False,
                                        parse_tests_queries  = False,
                                        import_patterns      = imports_f)

                return import_cond_dict

            # TESTs + RECURSIVE MODE:
            elif operational_conditions['read_test'] and operational_conditions['recursive_imports']:
                log.debug("Run test+recursive imports mode.")

                # Read test.py and extract query for future validation after addm scan and save model:
                # Later if -T in arg - use this, if no - just ignore.
                query_t = self.make_test_read_query()

                # Read test.py and extract list of patterns from self.setupPatterns
                # This is list of patterns I need to import from test.py.
                imports_t = TestRead(log).import_pattern_tests(self.working_dir,
                                                               self.tku_patterns_t)

                # Import tplpre's in recursive mode with extras from test.py:
                imports_f = self.make_imports(local_conditions = local_conditions,
                                              extra_patterns   = imports_t)

                import_cond_dict = dict(parse_tests_patterns = False,
                                        parse_tests_queries  = query_t,
                                        import_patterns      = imports_f)

                return import_cond_dict

            # SOLO MODE:
            elif not operational_conditions['read_test'] and \
                    not operational_conditions['recursive_imports'] and \
                    not operational_conditions['usual_imports']:

                log.info("There are no dev arguments found for Test read, or imports, or recursive imports. "
                         "Using as standalone tplpre.")

                import_cond_dict = dict(parse_tests_patterns = False,
                                        parse_tests_queries  = False,
                                        import_patterns      = False)

                return import_cond_dict

        elif environment_condition == 'customer_tku':

            if operational_conditions['recursive_imports']:
                log.info("Imports logic working in customer mode.")

                # Import tplpre's in recursive mode:
                imports_f = self.make_imports(local_conditions = local_conditions,
                                              extra_patterns   = None)

                import_cond_dict = dict(parse_tests_patterns = False,
                                        parse_tests_queries  = False,
                                        import_patterns      = imports_f)
                return import_cond_dict
            else:
                log.info("Working in customer mode, all other importing option will be ignored.")
        return import_cond_dict

    def preproc_cond(self, **logical_conditions):
        """
        Based on conditional args - run Preproc with import folder
        after my own method, or usual preproc method or even solo pattern preproc.

        Ignore step in customer mode.

        :param logical_conditions: set
        :return: func
        """
        log = self.logging

        # Set examples in __init__ docstrings:
        operational_conditions = logical_conditions['operational_conditions']
        environment_condition  = logical_conditions['local_conditions']['environment_condition']

        if environment_condition == 'developer_tplpre':
            # Preproc on NORMAL IMPORTS
            if operational_conditions['usual_imports'] and \
                    not operational_conditions['recursive_imports'] and \
                    not operational_conditions['read_test']:

                log.info("TPLPreprocessor will run on active file and import by its own logic.")
                preproc_f = self.make_preproc(workspace   = self.workspace,
                                              input_path  = self.full_path,
                                              output_path = self.working_dir,
                                              mode        = "usual_imports")

            # Preproc will run on all files from folder 'imports'
            elif operational_conditions['recursive_imports'] or operational_conditions['read_test'] and \
                    not operational_conditions['usual_imports']:

                log.info("TPLPreprocessor will run on imports folder after my importing logic.")
                # After R imports are finish its work - run TPLPreprocessor on it
                preproc_f = self.make_preproc(workspace   = self.workspace,
                                              input_path  = self.working_dir+os.sep+"imports",
                                              output_path = self.working_dir+os.sep+"imports",
                                              mode        = "recursive_imports")

            # SOLO MODE:
            elif not operational_conditions['read_test'] and \
                    not operational_conditions['recursive_imports'] and \
                    not operational_conditions['usual_imports']:
                log.info("TPLPreprocessor will run on active file without any additional imports.")

                preproc_f = self.make_preproc(workspace   = self.workspace,
                                              input_path  = self.full_path,
                                              output_path = self.working_dir,
                                              mode        = "solo_mode")

            return preproc_f
        elif environment_condition == 'customer_tku':
            log.debug("Ignoring TPLPreprocessor on customer_tku enviroment execution. All files should be tpl.")
            return False

    def syntax_cond(self, **logical_conditions):
        """
        Run syntax with options based on conditional arguments.

        If ADDM did not return any version - syntax check will run for all available versions.
        Optional: arg set of tpl version can be used here.

        By default - results printed in raw mode. Further execuion continues.

        :param logical_conditions: set
        :return: func
        """
        log = self.logging

        # Set examples in __init__ docstrings:
        operational_conditions = logical_conditions['operational_conditions']
        environment_condition  = logical_conditions['local_conditions']['environment_condition']
        tpl_version            = logical_conditions['tpl_version']

        # Preproc on NORMAL IMPORTS
        if operational_conditions['usual_imports']:

            log.info("Syntax check will run on tpl folders after usual TPLPreproc output.")

            # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
            syntax_check_f = self.make_syntax_check(self.working_dir, disco_ver=tpl_version)

        # Preproc will run on all files from folder 'imports'
        elif operational_conditions['recursive_imports'] or operational_conditions['read_test']:

            log.info("Syntax check will run on imports folder after my importing logic.")

            # After TPLPreprocessor finished its work - run Syntax Check on folder imports
            # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
            syntax_check_f = self.make_syntax_check(self.working_dir+os.sep+"imports",
                                                    disco_ver=tpl_version)

        # SOLO MODE:
        elif not operational_conditions['read_test'] and \
                not operational_conditions['recursive_imports'] and \
                not operational_conditions['usual_imports']:

            log.info("1/1 Syntax check will run on active file without any additional imports.")
            log.debug("1/2 This means that all imports was already created and you just want to check syntax for active pattern.")

            # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
            # In this condition syntax check will hope that imports are already in folder after previous runs.
            syntax_check_f = self.make_syntax_check(self.working_dir,
                                                    disco_ver=tpl_version)

        return syntax_check_f

    def addm_dev_cond(self, addm_vm_condition, environment_condition):
        """
        Based on args - make decision is ADDM dev or not - and compose paths for DEV or not.

        :type environment_condition: str
        :type addm_vm_condition: str
        :return: paths
        """
        log = self.logging

        # Set examples in __init__ docstrings:
        if environment_condition == 'developer_tplpre':
            if addm_vm_condition:
                log.info("DEV ADDM is working - files will be activated in mirrored filesystem.")

                # Compose paths:
                local_logic = LocalLogic(log)
                addm_working_dir = local_logic.addm_compose_paths(dev_vm_path    = self.dev_vm_path,
                                                                  pattern_folder = self.full_path_args['pattern_folder'])

            elif not addm_vm_condition:
                log.info("Usual ADDM is working - files will be uploaded to '/usr/tideway/TKU/Tpl_DEV/' folder and activated.")
                addm_working_dir = '/usr/tideway/TKU/Tpl_DEV'
        elif environment_condition == 'customer_tku':
            addm_working_dir = '/usr/tideway/TKU/Tpl_DEV'
            log.debug("This is a customer mode, files will be uploaded to hardcoded path: "+str(addm_working_dir))

        return addm_working_dir

    def pattern_path_cond(self, **logical_conditions):
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

        # Set examples in __init__ docstrings:
        addm_conditions        = logical_conditions['addm_conditions']
        addm_vm_condition      = addm_conditions['dev_vm_check']
        operational_conditions = logical_conditions['operational_conditions']
        addm_working_dir       = logical_conditions['addm_working_dir']
        local_conditions       = logical_conditions['local_conditions']
        environment_condition  = local_conditions['environment_condition']

        # Based on imports mode:
        if operational_conditions['usual_imports'] or operational_conditions['recursive_imports']:
            log.debug("Making zip from imported patterns.")

            # Include 'imports' dir into the path:
            imports_dir = os.sep+"imports"+os.sep

            # Path of active pattern folder + imports dir + tpl<version dir>(or not is customer):
            if environment_condition == 'developer_tplpre':
                path_to_result = self.full_path_args['working_dir']+imports_dir+self.tpl_folder+os.sep
            elif environment_condition == 'customer_tku':
                path_to_result = self.full_path_args['working_dir']+imports_dir

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
                # local_zip: d:\workspace\addm\tkn_main\tku_patterns\CORE\PatternName\imports\tpl113\PatternName.zip
                local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                log.debug("local_zip: "+str(local_zip))
            else:
                # I do not use this, because I want to zip files without uploading:
                addm_result_folder = addm_working_dir
                # Just make zip on local files and don't move it:
                local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                log.debug("local_zip: "+str(local_zip))


            # In dev mode I have pattern folder as name and result path to tpl after Preproc:
            if environment_condition == 'developer_tplpre':
                addm_zip_f = self.make_zip(path_to_result=path_to_result,
                                           active_folder=self.full_path_args['pattern_folder'])
                # Making function obj for ZIP
                zip_mirror = addm_result_folder+"/"+self.full_path_args['pattern_folder'] + '.zip'
            # In customer mode I have just only inports folder and pattern name for module naming:
            elif environment_condition == 'customer_tku':
                addm_zip_f = self.make_zip(path_to_result=path_to_result,
                                           active_folder=local_conditions['file_name'])
                # Rewrite addm zip path to hardcoded:
                zip_mirror = addm_working_dir +"/" +local_conditions['file_name']+ '.zip'
                addm_result_folder = 'Ignore HGFS on customer mode.'

            # Path to zip with import included:
            # path_to_zip: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName/imports/tpl113/PatternName.zip
            addm_zip = zip_mirror

            log.debug("addm_zip: "+str(addm_zip))
            log.debug("addm_result_folder: "+str(addm_result_folder))
            log.debug("path_to_result: "+str(path_to_result))

        elif not operational_conditions['usual_imports'] and not operational_conditions['recursive_imports']:
            log.debug("Imports condition - NOT DEV IMPORTS to addm: Making zip with one active file.")

            # Path of active pattern to ZIP:
            # 'working_dir': 'd:\\workspace\\addm\\tkn_main\\tku_patterns\\CORE\\PatternName',
            # path_to_result: d:\workspace\addm\tkn_main\tku_patterns\CORE\PatternName\tpl113\
            path_to_result = self.full_path_args['working_dir']+os.sep+self.tpl_folder+os.sep

            # Pattern remote path in ADDM FS:
            # addm_zip_path = addm_working_dir+"/"+self.tpl_folder+"/"+self.full_path_args['file_name']+".tpl"

            # Pattern remote path in ADDM FS:
            if addm_vm_condition:
                # On DEV ADDM (example docs: remote(mirror)):
                # addm_result_folder: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName/tpl113
                addm_result_folder = addm_working_dir+"/"+self.tpl_folder
                # I do not need this, because on DEV VM I will just activate zip in mirror FS
                local_zip = 'ADDM is in DEV mode - not need to point to local zip file.'
            elif not addm_vm_condition:
                # Not on DEV ADDM (example docs: remote(not DEV)): /usr/tideway/TKU/Tpl_DEV/
                # addm_result_folder: /usr/tideway/TKU/Tpl_DEV
                addm_result_folder = addm_working_dir
                # local_zip: d:\workspace\addm\tkn_main\tku_patterns\CORE\PatternName\tpl113\PatternName.zip
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
            # addm_zip: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName/tpl113/PatternName.zip
            addm_zip = zip_remote

            log.debug("addm_zip: "+str(addm_zip))
            log.debug("addm_result_folder: "+str(addm_result_folder))
            log.debug("path_to_result: "+str(path_to_result))

        return addm_zip_f, addm_zip, local_zip

    def zip_activ_cond(self, **zipping_conditions):
        """
        Based on ADDM state - if DEV_VM or not - choose folder where activate or upload and activate ZIP with patterns.
        In case of customer run - addm dev option will be ignored.

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
        :param zipping_conditions: set
        :return: upload_f, addm_activate_f
        """
        log = self.logging

        # Set examples in __init__ docstrings:
        addm_conditions   = zipping_conditions['addm_conditions']
        addm_zip          = zipping_conditions['addm_zip']
        local_zip         = zipping_conditions['local_zip']
        local_conditions  = zipping_conditions['local_conditions']

        pattern_file_name = local_conditions['file_name']
        pattern_folder    = local_conditions['pattern_folder']

        addm_vm_condition = addm_conditions['dev_vm_check']
        # From args, of not set - use default system\system
        system_user           = addm_conditions['system_user']
        system_password       = addm_conditions['system_password']
        environment_condition = local_conditions['environment_condition']

        if environment_condition == 'developer_tplpre':
            if addm_vm_condition:
                # Just activate zip in mirrored path:
                log.info("Files will be activated in mirrored filesystem.")
                addm_activate_f = self.make_activate_zip(zip_path        = addm_zip,
                                                         module_name     = pattern_folder,
                                                         system_user     = system_user,
                                                         system_password = system_password)
                upload_f = False

            elif not addm_vm_condition:
                # Upload zip to addm custom folder and then activate:
                log.info("Files will be uploaded to '/usr/tideway/TKU/Tpl_DEV/' folder and then activated.")

                # UPLOAD zip to ADDM via SFTP:
                upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)

                addm_activate_f = self.make_activate_zip(zip_path        = addm_zip,
                                                         module_name     = pattern_folder,
                                                         system_user     = system_user,
                                                         system_password = system_password)
        elif environment_condition == 'customer_tku':
            log.info("Files will be uloaded in '/usr/tideway/TKU/Tpl_DEV/' folder.")

            # UPLOAD zip to ADDM via SFTP:
            upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)

            addm_activate_f = self.make_activate_zip(zip_path        = addm_zip,
                                                     module_name     = pattern_file_name,
                                                     system_user     = system_user,
                                                     system_password = system_password)

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

    def make_imports(self, **condition_kwargs):
        """
        Closure for imports function.
        Version for customer run.
        Based or arguments - decide which import will run.
        Or nothing to run at all.

        :return: func with imports
        """
        log = self.logging


        def importer():
            tpl_imports = TPLimports(log, self.full_path_args)
            # Now I don't need args because class was initialized with args above:
            tpl_imports.import_modules(conditions=condition_kwargs)
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
    
    def make_activate_zip(self, zip_path, module_name, system_user, system_password):
        """
        Closure for pattern activation.
        Input arg to zip path - can be local or remote.

        :type system_user: str
        :type system_password: str
        :type module_name: str
        :type zip_path: str
        :return: func
        """
        log = self.logging

        def activate():
            addm = AddmOperations(log, self.ssh)
            # Activate zip package using path from arg (local|remote):
            addm.activate_knowledge(zip_path, module_name, system_user, system_password)

        return activate
    
    def make_scan(self, addm_conditions, module_name):
        """
        Closure for addm start scan function with args.

        addm_conditions: {
                          "dev_vm_path": "/usr/tideway/TKU",
                          "addm_prod": "Bobblehat",
                          "dev_vm_check": true,
                          "ssh_connection": "<paramiko.client.SSHClient object at 0x00000000035E30F0>",
                          "tpl_vers": "1.13",
                          "system_user": "system",
                          "tpl_folder": "tpl113",
                          "addm_ver": "11.1",
                          "disco_mode": "record",
                          "scan_hosts": "172.25.144.95, 172.25.144.39",
                          "system_password": "system"
                          }

        :type module_name: str
        :type host_list: str
        :type disco_mode: str
        :return: func
        """
        log = self.logging

        disco_mode      = addm_conditions['disco_mode']
        host_list       = addm_conditions['scan_hosts']
        system_user     = addm_conditions['system_user']
        system_password = addm_conditions['system_password']

        def scan():
            addm_scan = AddmScan(log, self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm_scan.addm_scan(disco_mode,
                                host_list,
                                system_user,
                                system_password,
                                module_name)

        return scan