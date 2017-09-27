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

import logging
log = logging.getLogger("check.logger")

class GlobalLogic:

    def __init__(self, extra_args, known_args, **kwargs):
        """
        Initialize with options for logical operations.
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

        :rtype: func
        :param kwargs:
        """
        # TODO: assign most args here, no need to re-assign them each time in func().
        # Anyway this class should initialize with all available options or throw an exception



        # Get all available arguments in three sets based on its type:
        self.full_path_args, \
        self.operational_args, \
        self.addm_args_set = self.check_args_set(known_args =known_args,
                                                 extra_args =extra_args)

        # DEBUG
        # import json
        # from pprint import pformat
        # print(json.dumps(self.addm_args_set, indent=4, ensure_ascii=False, default=pformat))

        # Check args in init module to further assign on function bodies:
        assert isinstance(self.full_path_args, dict)
        if self.full_path_args:
            '''
                Examples of arg sets
        
                    PATH ARGS: {
                        "BLADE_ENCLOSURE_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-BladeEnclosure-2017-07-1-ADDM-11.1+",
                        "SYSTEM_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-System-2017-07-1-ADDM-11.1+",
                        "tkn_main_t": "",
                        "tku_patterns_t": "",
                        "MIDDLEWAREDETAILS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+",
                        "workspace": "D:\\TKU",
                        "file_name": "PatternName",
                        "CLOUD_t": "",
                        "full_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Core-2017-07-1-ADDM-11.1+\\PatternName.tpl",
                        "DBDETAILS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+",
                        "working_dir": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Core-2017-07-1-ADDM-11.1+",
                        "CORE_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Core-2017-07-1-ADDM-11.1+",
                        "file_ext": "tpl",
                        "pattern_folder": "TKU-Core-2017-07-1-ADDM-11.1+",
                        "MANAGEMENT_CONTROLLERS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-ManagementControllers-2017-07-1-ADDM-11.1+",
                        "STORAGE_t": "",
                        "buildscripts_t": "",
                        "environment_condition": "customer_tku",
                        "LOAD_BALANCER_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-LoadBalancer-2017-07-1-ADDM-11.1+",
                        "tkn_sandbox_t": ""
                    }
        
                    PATH ARGS:
                            {
                            "MANAGEMENT_CONTROLLERS_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\MANAGEMENT_CONTROLLERS",
                            "CLOUD_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\CLOUD",
                            "BLADE_ENCLOSURE_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\BLADE_ENCLOSURE",
                            "file_name": "BMCRemedyARSystem",
                            "tkn_sandbox_t": "d:\\perforce\\addm\\tkn_sandbox",
                            "tku_patterns_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns",
                            "LOAD_BALANCER_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\LOAD_BALANCER",
                            "CORE_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE",
                            "SYSTEM_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\SYSTEM",
                            "STORAGE_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\STORAGE",
                            "working_dir": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem",
                            "DBDETAILS_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS",
                            "pattern_folder": "BMCRemedyARSystem",
                            "file_ext": "tplpre",
                            "environment_condition": "developer_tplpre",
                            "tkn_main_t": "d:\\perforce\\addm\\tkn_main",
                            "pattern_test_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem\\tests\\test.py",
                            "buildscripts_t": "d:\\perforce\\addm\\tkn_main\\buildscripts",
                            "full_path": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem\\BMCRemedyARSystem.tplpre",
                            "workspace": "d:\\perforce",
                            "MIDDLEWAREDETAILS_t": "d:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS"
                            }

            '''

            self.tku_patterns_t = self.full_path_args['tku_patterns_t']
            self.workspace      = self.full_path_args['workspace']
            self.full_path      = self.full_path_args['full_path']
            self.working_dir    = self.full_path_args['working_dir']

            if not self.working_dir:
                log.error("File working dir is not extracted - I cannot proceed any function.")

            log.debug("Full path arguments are set. It will be used to choose program working scenario.")
        else:
            log.critical("No full path arguments were set. I can do nothing with this.")
            msg = "There is no -full_path argument set or it cannot be parsed."
            raise Error(msg)

        assert isinstance(self.addm_args_set, dict)
        if self.addm_args_set:
            '''
            ADDM VM ARGS: {
                            "scan_hosts": false,
                            "dev_vm_check": true,
                            "ssh_connection": "<paramiko.client.SSHClient object at 0x0000000003343128>",
                            "system_password": "system",
                            "addm_prod": "Bobblehat",
                            "system_user": "system",
                            "dev_vm_path": "/usr/tideway/TKU",
                            "tpl_vers": "1.13",
                            "tpl_folder": "tpl113",
                            "disco_mode": "",
                            "addm_ver": "11.1"
                            }
            '''

            self.ssh            = self.addm_args_set['ssh_connection']
            self.tpl_folder     = self.addm_args_set['tpl_folder']
            self.dev_vm_path    = self.addm_args_set['dev_vm_path']

            log.debug("ADDM arguments are gathered from addm host. "
                      "It will be used to choose program working scenario.")
        else:
            log.debug("ADDM arguments are gathered or wasn't set. Program will work on local mode.")

        assert isinstance(self.operational_args, dict)

        if self.operational_args['imports']:
            '''
                {'recursive_imports': False, 
                'read_test': False, 
                'run_test': True, 
                'related_tests': False, 
                'usual_imports': False}

            '''

            self.recursive_imports = self.operational_args['imports']['recursive_imports']
            self.usual_imports     = self.operational_args['imports']['usual_imports']
            self.read_test         = self.operational_args['imports']['read_test']

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
                log.debug("Import arguments was not set: "+str(self.operational_args['imports']))
        else:
            log.debug("Import arguments was not set: "+str(self.operational_args['imports']))
            log.debug("Import arguments are set to False.")

            self.recursive_imports = False
            self.usual_imports     = False
            self.read_test         = False

        if self.operational_args['tests']:
            self.related_tests     = self.operational_args['tests']['related_tests']
            self.run_test          = self.operational_args['tests']['run_test']

            if self.related_tests and not self.run_test:
                log.debug("Will find all related tests for this pattern.")
            elif self.run_test and not self.related_tests:
                log.debug("Will run test for this pattern.")
            else:
                log.debug("No tests will run. "+str(self.operational_args['tests']))
        else:
            log.debug("No test runs.")
            self.related_tests = False
            self.run_test      = False

    def check_args_set(self, **args_from_cmd):
        """
        This will check args set in input.
        Based on set of args - it will compose another set of functions.
        The set of functions will consist of all needed functions on order to execute.

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

        :param args_from_cmd: set
        :return:
        """
        parse_args = ArgsParse()

        return parse_args.gather_args(known_args=args_from_cmd['known_args'],
                                      extra_args=args_from_cmd['extra_args'])


    def make_function_set(self) -> object:
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

        :rtype: object
        :return: pair of function sets with conditional functions to execute and result to debug.
        """

        conditional_functions, conditional_results = self.cond_args(addm_args_set    = self.addm_args_set,
                                                                    full_path_args   = self.full_path_args,
                                                                    operational_args = self.operational_args)


        return conditional_functions, conditional_results

# Doing business based on all decisions made:
    def cond_args(self, **args_set):
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
        assert isinstance(args_set, dict)

        # Set examples in __init__ docstrings:
        addm_conditions        = args_set['addm_args_set']
        assert isinstance(addm_conditions, dict)

        local_conditions       = args_set['full_path_args']
        assert isinstance(local_conditions, dict)

        operational_args       = args_set['operational_args']
        assert isinstance(operational_args, dict)

        import_conditions      = operational_args['imports']
        test_conditions        = operational_args['tests']
        tku_operations         = operational_args['tku_operations']
        # Wipe TKU?
        tku_wipe_flag          = tku_operations['wipe_tku']


        # Set operational option for dev or customer:
        environment_condition = local_conditions['environment_condition']
        log.debug("Program's global logic module operating in: '"+str(environment_condition)+"' mode.")

        # This will be re-write if success:
        imports_f                   = False
        preproc_f                   = False
        syntax_check_f              = False
        zip_files_f                 = False
        addm_activate_f             = False
        upload_f                    = False
        scan_f                      = False
        test_executor_f             = False

        addm_zip                    = ''
        local_zip                   = ''
        addm_working_dir            = ''

        upload_scan                 = False
        local_proceed_for_addm      = False
        upload_only                 = False
        wipe_tku_f                  = False
        import_preproc_syntax_local = False
        tests_run                   = False

        # import json
        # from pprint import pformat
        # print(json.dumps(addm_conditions, indent=4, ensure_ascii=False, default=pformat))
        # print(json.dumps(local_conditions, indent=4, ensure_ascii=False, default=pformat))
        # print(json.dumps(operational_args, indent=4, ensure_ascii=False, default=pformat))
        # print(json.dumps(import_conditions, indent=4, ensure_ascii=False, default=pformat))

        # TODO: Debug disable:
        # noinspection PyUnusedLocal
        import_conditions_debug = dict(read_test         = False,
                                       recursive_imports = True,
                                       usual_imports     = False)

        # noinspection PyUnusedLocal
        addm_conditions_debug = dict(
                                    disco_mode      = "record",
                                    system_password = "system",
                                    tpl_vers        = "1.13",
                                    addm_prod       = "Bobblehat",
                                    tpl_folder      = "tpl113",
                                    addm_ver        = "11.1",
                                    system_user     = "system",
                                    # dev_vm_path     = "/usr/tideway/TKU",
                                    dev_vm_path     = "/usr/tideway/TKU/Tpl_DEV/",
                                    dev_vm_check    = True,
                                    ssh_connection  = addm_conditions['ssh_connection'],
                                    scan_hosts      = False
                                    )

        # addm_conditions = addm_conditions_debug
        # import_conditions = import_conditions_debug

        # Addm args for scan
        # TODO: What if declare each this if AS functional dict splitted for each situation?
        if addm_conditions['scan_hosts'] and addm_conditions['disco_mode'] and addm_conditions['ssh_connection'] \
                and not test_conditions:

            log.info("ADDM Scan action.")
            log.debug("ADDM Scan args are present, current files will be uploaded to ADDM and Scan will be started.")

            upload_scan = True

        elif not addm_conditions['disco_mode'] and not addm_conditions['scan_hosts'] and addm_conditions['tpl_folder'] \
                and addm_conditions['ssh_connection'] \
                and not test_conditions:

            log.info("No ADDM action. Local processing")
            log.debug("No ADDM Scan and discovery args are present. "
                      "Local processing with tpl version gathered from live ADDM.")

            local_proceed_for_addm = True

        elif not addm_conditions['scan_hosts'] and addm_conditions['tpl_folder'] and addm_conditions['disco_mode'] \
                and addm_conditions['ssh_connection'] \
                and not test_conditions:

            log.info("ADDM Upload. No scan.")
            log.debug("ADDM Upload args are present, current files will be uploaded to ADDM. No scan.")

            upload_only = True

        elif not addm_conditions['ssh_connection'] and not test_conditions:

            log.info("Local processing. No ADDM connection.")
            import_preproc_syntax_local = True

        elif addm_conditions['ssh_connection'] and test_conditions:

            tests_run = True
            log.debug("ADDM SSH Connections is active and test run was set.")
        # I don't know:
        else:
            log.info("This set of conditional arguments is not supported by my logic, Please read docs.")


        # TODO: Maybe better to use IFs in separate function jus for if, and declare modes. Or this can be over-minded?
        if upload_scan:
            log.info("Upload and scan.")
            # Import patterns if needed on mode set in import_conditions
            imports_f = self.imports_cond(import_conditions = import_conditions,
                                          local_conditions  = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(import_conditions = import_conditions,
                                          local_conditions  = local_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_args = operational_args,
                                              tpl_version       = addm_conditions['addm_ver'],
                                              local_conditions  = local_conditions)

            # Generate addm working dir based on DEV condition:
            addm_working_dir, tests_path = self.addm_dev_cond(addm_conditions['dev_vm_check'],
                                                              environment_condition)

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            zip_files_f, addm_zip, local_zip = self.pattern_path_cond(addm_vm_condition = addm_conditions['dev_vm_check'],
                                                                      import_conditions = import_conditions,
                                                                      addm_working_dir  = addm_working_dir,
                                                                      local_conditions  = local_conditions)
            # If you want to wipe all TKU before:
            if tku_wipe_flag:
                wipe_tku_f = self.make_tku_wiping(system_user=addm_conditions['system_user'],
                                                  system_password=addm_conditions['system_password'])


            # Using path to zip result from above - activate it in ADDM
            upload_f, addm_activate_f = self.zip_activ_cond(addm_conditions  = addm_conditions,
                                                            addm_zip         = addm_zip,
                                                            local_zip        = local_zip,
                                                            local_conditions = local_conditions)

            # Start scan action:
            # Better to use filename as active file - which initiates this run:
            scan_f = self.make_scan(addm_conditions = addm_conditions,
                                    module_name     = self.full_path_args['file_name'])
        # When I have no args for scan AND NO args for ADDM disco,
        # but have arg for tpl_vers - proceed files locally with that version.
        elif local_proceed_for_addm:
            log.info("Local processing based on args from ADDM.")
            # Import patterns if needed on mode set in import_conditions
            imports_f = self.imports_cond(import_conditions = import_conditions,
                                          local_conditions  = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(import_conditions = import_conditions,
                                          local_conditions  = local_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_args = operational_args,
                                              tpl_version       = addm_conditions['addm_ver'],
                                              local_conditions  = local_conditions)

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            addm_working_dir = 'Null'
            zip_files_f, addm_zip, local_zip = self.pattern_path_cond(addm_vm_condition = None,
                                                                      import_conditions = import_conditions,
                                                                      addm_working_dir  = addm_working_dir,
                                                                      local_conditions  = local_conditions)
            # tpl_vers addm_prod addm_ver
            log.info("Zipped for ADDM: "+str(addm_conditions['addm_prod'])+
                     " Ver. "+str(addm_conditions['addm_ver'])+
                     " Tpl v. "+str(addm_conditions['tpl_vers']))

        # When I have NO args for Scan, but have args for ADDM status and disco - will start upload only.
        elif upload_only:
            log.info("Upload only.")
            # Import patterns if needed on mode set in import_conditions
            imports_f = self.imports_cond(import_conditions = import_conditions,
                                          local_conditions = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(import_conditions = import_conditions,
                                          local_conditions  = local_conditions)

            # Run syntax check based on cond args:
            syntax_check_f = self.syntax_cond(operational_args = operational_args,
                                              tpl_version       = addm_conditions['addm_ver'],
                                              local_conditions  = local_conditions)

            # Generate addm working dir based on DEV condition:
            addm_working_dir, tests_path = self.addm_dev_cond(addm_conditions['dev_vm_check'],
                                                              environment_condition)

            # Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
            zip_files_f, addm_zip, local_zip = self.pattern_path_cond(addm_vm_condition = addm_conditions['dev_vm_check'],
                                                                      import_conditions = import_conditions,
                                                                      addm_working_dir  = addm_working_dir,
                                                                      local_conditions  = local_conditions)

            # If you want to wipe all TKU before:
            if tku_wipe_flag:
                wipe_tku_f = self.make_tku_wiping(system_user=addm_conditions['system_user'],
                                                  system_password=addm_conditions['system_password'])

            # Using path to zip result from above - activate it in ADDM
            upload_f, addm_activate_f = self.zip_activ_cond(addm_conditions = addm_conditions,
                                                            addm_zip        = addm_zip,
                                                            local_zip       = local_zip,
                                                            local_conditions = local_conditions)
            log.info("Zipped for ADDM: "+str(addm_conditions['addm_prod'])+
                     " Ver. "+str(addm_conditions['addm_ver'])+
                     " Tpl v. "+str(addm_conditions['tpl_vers']))
            # No Scan action because: not addm_conditions['scan_hosts'] just upload and activate.

        # No addm args:
        elif import_preproc_syntax_local:
            # I have no active connection to ADDM so I don't know about tpl version to generate and zip
            #  - SO I will just import, Preproc and check syntax


            # Import patterns if needed on mode set in import_conditions
            imports_f = self.imports_cond(import_conditions = import_conditions,
                                          local_conditions = local_conditions)

            # Run preproc on patterns based on conditional arguments:
            preproc_f = self.preproc_cond(import_conditions = import_conditions,
                                          local_conditions  = local_conditions)

            # Run syntax check based on cond args:
            # Maybe I can add tpl_version for offline checks but what for?
            syntax_check_f = self.syntax_cond(operational_args = operational_args,
                                              tpl_version       = '',
                                              local_conditions  = local_conditions)

            addm_zip         = 'There is no ADDM connection, program is running in local mode.'
            local_zip        = 'There is no ADDM connection, program is running in local mode.'
            addm_working_dir = 'There is no ADDM connection, program is running in local mode.'

        # When ADDM connection is present and test options used:
        elif tests_run:
            test_executor_f = self.test_run_cond(test_conditions=test_conditions,
                                                 addm_conditions=addm_conditions,
                                                 environment_condition=environment_condition)

        # I don't know:
        else:
            log.warning("I can't understand the logic of current set of options. Printing "
                        "\noperational_args: "+str(operational_args)+
                        "\naddm_args_set: "+str(addm_args_set)+
                        "\nfull_path_args: "+str(full_path_args))

        # TODO: Better update each key in correspond tree?
        conditional_functions = dict(imports_f       = imports_f,
                                     preproc_f       = preproc_f,
                                     syntax_check_f  = syntax_check_f,
                                     zip_files_f     = zip_files_f,
                                     wipe_tku_f      = wipe_tku_f,
                                     upload_f        = upload_f,
                                     addm_activate_f = addm_activate_f,
                                     scan_f          = scan_f,
                                     test_executor_f = test_executor_f)

        conditional_results = dict(addm_zip         = addm_zip,
                                   local_zip        = local_zip,
                                   addm_working_dir = addm_working_dir)

        return conditional_functions, conditional_results


# Functions to make decisions based on options and create closures.
    def imports_cond(self, **logical_conditions):
        """
        Based on condition arguments use different scenarios of importing patterns:

        Including customer condition it now will decide how to import patterns.

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

        :param logical_conditions: mode to operate with - dev or customer.
        :return:
        """

        assert isinstance(logical_conditions, dict)
        # Set examples in __init__ docstrings:
        import_conditions      = logical_conditions['import_conditions']
        environment_condition  = logical_conditions['local_conditions']['environment_condition']
        local_conditions       = logical_conditions['local_conditions']

        import_cond_dict = dict(parse_tests_patterns=False,
                                parse_tests_queries=False,
                                import_patterns=False)

        assert isinstance(environment_condition, str)
        assert isinstance(local_conditions, dict)

        if isinstance(import_conditions, dict):
            if environment_condition == 'developer_tplpre':
                # NORMAL IMPORTS
                if import_conditions['usual_imports']:
                    log.info("No extra imports. TPLPreprocessor will import.")

                    import_cond_dict = dict(parse_tests_patterns=False,
                                            parse_tests_queries=False,
                                            import_patterns=False)

                    return import_cond_dict

                # RECURSIVE MODE:
                elif import_conditions['recursive_imports'] and \
                        not import_conditions['read_test']:
                    log.info("Run recursive imports mode.")

                    # Import tplpre's in recursive mode:
                    imports_f = self.make_imports(local_conditions = local_conditions,
                                                  extra_patterns   = None)

                    import_cond_dict = dict(parse_tests_patterns = False,
                                            parse_tests_queries  = False,
                                            import_patterns      = imports_f)

                    return import_cond_dict

                # TESTs + RECURSIVE MODE:
                elif import_conditions['read_test'] and import_conditions['recursive_imports']:
                    log.info("Run test+recursive imports mode.")

                    # Read test.py and extract query for future validation after addm scan and save model:
                    # Later if -T in arg - use this, if no - just ignore.
                    query_t = self.make_test_read_query()

                    # Read test.py and extract list of patterns from self.setupPatterns
                    # This is list of patterns I need to import from test.py.
                    imports_t = TestRead().import_pattern_tests(self.working_dir)

                    # Import tplpre's in recursive mode with extras from test.py:
                    imports_f = self.make_imports(local_conditions = local_conditions,
                                                  extra_patterns   = imports_t)

                    import_cond_dict = dict(parse_tests_patterns = False,
                                            parse_tests_queries  = query_t,
                                            import_patterns      = imports_f)

                    return import_cond_dict

                # SOLO MODE:
                elif not import_conditions['read_test'] and \
                        not import_conditions['recursive_imports'] and \
                        not import_conditions['usual_imports']:

                    log.debug("There are no dev arguments found for Test read, or imports, or recursive imports.")
                    log.info("Using as standalone tplpre.")

                    import_cond_dict = dict(parse_tests_patterns = False,
                                            parse_tests_queries  = False,
                                            import_patterns      = False)

                    return import_cond_dict

            elif environment_condition == 'customer_tku':

                if import_conditions['recursive_imports']:
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
        else:
            log.debug("No import options passed.")


        return import_cond_dict

    def preproc_cond(self, **logical_conditions):
        """
        Based on conditional args - run Preproc with import folder
        after my own method, or usual preproc method or even solo pattern preproc.

        Ignore step in customer mode.

        :param logical_conditions: set
        :return: func
        """

        # TODO: Check condition groups
        assert isinstance(logical_conditions, dict)
        # Assign
        preproc_f = False

        # Set examples in __init__ docstrings:
        import_conditions = logical_conditions['import_conditions']
        environment_condition  = logical_conditions['local_conditions']['environment_condition']

        if environment_condition == 'developer_tplpre':
            if isinstance(import_conditions, dict):
                # Preproc on NORMAL IMPORTS
                # TODO: Make decisional functions and move all those decisions to them, so I can just call it and know wnat mode to run!
                if import_conditions['usual_imports'] and not import_conditions['recursive_imports'] and \
                        not import_conditions['read_test']:

                    log.info("TPLPreprocessor run on pattern and import.")
                    log.debug("TPLPreprocessor will run on active file and import by its own logic. (usual_imports)")
                    preproc_f = self.make_preproc(workspace   = self.workspace,
                                                  input_path  = self.full_path,
                                                  output_path = self.working_dir,
                                                  mode        = "usual_imports")
                    return preproc_f

                # Preproc will run on all files from folder 'imports'
                elif import_conditions['recursive_imports'] or import_conditions['read_test'] and \
                        not import_conditions['usual_imports']:

                    log.info("TPLPreprocessor run on imports folder.")
                    log.debug("TPLPreprocessor will run on imports folder after my recursive importing logic. (recursive_imports)")
                    # After R imports are finish its work - run TPLPreprocessor on it
                    preproc_f = self.make_preproc(workspace   = self.workspace,
                                                  input_path  = self.working_dir+os.sep+"imports",
                                                  output_path = self.working_dir+os.sep+"imports",
                                                  mode        = "recursive_imports")
                    return preproc_f
            # SOLO mode:
            else:
                log.info("TPLPreprocessor run on pattern without imports.")
                log.debug("TPLPreprocessor will run on active file without any additional imports. (solo_mode)")

                preproc_f = self.make_preproc(workspace   = self.workspace,
                                              input_path  = self.full_path,
                                              output_path = self.working_dir,
                                              mode        = "solo_mode")

                return preproc_f

        elif environment_condition == 'customer_tku':
            log.debug("Ignoring TPLPreprocessor on customer_tku environment execution. All files should be tpl.")
            return False

    def syntax_cond(self, **logical_conditions):
        """
        Run syntax with options based on conditional arguments.

        If ADDM did not return any version - syntax check will run for all available versions.
        Optional: arg set of tpl version can be used here.

        By default - results printed in raw mode. Further execution continues.

        {
            "operational_args": {
                "tku_operations": {
                    "wipe_tku": false
                },
                "tests": false,
                "imports": false
            },
            "tpl_version": "11.1",
            "local_conditions": {
                "STORAGE_t": "",
                "buildscripts_t": "",
                "tkn_sandbox_t": "",
                "environment_condition": "customer_tku",
                "full_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+\\BMCRemedyARSystem.tpl",
                "pattern_folder": "TKU-Core-2017-07-1-ADDM-11.1+",
                "DBDETAILS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+",
                "CORE_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+",
                "LOAD_BALANCER_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-LoadBalancer-2017-07-1-ADDM-11.1+",
                "workspace": "D:\\TKU",
                "MANAGEMENT_CONTROLLERS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+",
                "tku_patterns_t": "",
                "CLOUD_t": "",
                "working_dir": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+",
                "MIDDLEWAREDETAILS_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+",
                "file_name": "BMCRemedyARSystem",
                "BLADE_ENCLOSURE_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+",
                "tkn_main_t": "",
                "file_ext": "tpl",
                "SYSTEM_t": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-System-2017-07-1-ADDM-11.1+"
            }
        }

        :param logical_conditions: set
        :return: func
        """
        # TODO: Check condition groups
        assert isinstance(logical_conditions, dict)

        # DEBUG
        # import json
        # from pprint import pformat
        # print(json.dumps(logical_conditions, indent=4, ensure_ascii=False, default=pformat))

        # Set examples in __init__ docstrings:
        tpl_version       = logical_conditions['tpl_version']
        import_conditions = logical_conditions['operational_args']['imports']
        environment_condition = logical_conditions['local_conditions']['environment_condition']

        syntax_check_f = False

        if isinstance(import_conditions, dict):
            # Preproc on NORMAL IMPORTS
            # TODO: Make decisional functions and move all those decisions to them, so I can just call it and know wnat mode to run!
            if import_conditions['usual_imports']:

                log.info("Syntax check TPLPreprocessor output.")
                log.debug("Syntax check will run on tpl folders after usual TPLPreproc output. (usual_imports)")

                # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
                syntax_check_f = self.make_syntax_check(self.working_dir, disco_ver=tpl_version)

            # Preproc will run on all files from folder 'imports'
            elif import_conditions['recursive_imports'] or import_conditions['read_test']:

                log.info("Syntax check on imports.")
                log.debug("Syntax check will run on imports folder after my importing logic. (recursive_imports or read_test)")

                # After TPLPreprocessor finished its work - run Syntax Check on folder imports
                # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
                syntax_check_f = self.make_syntax_check(self.working_dir+os.sep+"imports",
                                                        disco_ver=tpl_version)

        else:
            if environment_condition == 'developer_tplpre':
                log.info("1/1 Syntax check solo file.")
                log.debug("1/2 Imports was already created just checking syntax for active pattern. "
                          "(not read_test not recursive_imports not usual_imports)")
                # If no addm version - it will use empty string as arg and run syntax check for all supported versions.
                # In this condition syntax check will hope that imports are already in folder after previous runs.
                syntax_check_f = self.make_syntax_check(self.working_dir,
                                                        disco_ver=tpl_version)

            elif environment_condition == 'customer_tku':
                log.warning("TPLint cannot checl syntax for single tpl file!"
                            "On other way it will check syntax for whole CORE folder and this can take muck time."
                            "To check syntax please choose usual imports option, "
                            "so TPLLint will run it only for 'imports' folder!")

        return syntax_check_f

    def addm_dev_cond(self, addm_vm_condition, environment_condition):
        """
        Based on args - make decision is ADDM dev or not - and compose paths for DEV or not.

        :type environment_condition: str
        :type addm_vm_condition: str
        :return: paths
        """
        # Assign
        addm_wd = ''
        test_path = ''

        # Set examples in __init__ docstrings:
        if environment_condition == 'developer_tplpre':
            if addm_vm_condition:
                log.info("DEV ADDM - files activating in mirrored filesystem.")

                # Compose paths:
                local_logic = LocalLogic()
                addm_wd, test_path = local_logic.addm_compose_paths(dev_vm_path    = self.dev_vm_path,
                                                                    pattern_folder = self.full_path_args['pattern_folder'])

            elif not addm_vm_condition:
                log.info("Usual ADDM - files uploading: '/usr/tideway/TKU/Tpl_DEV/'")
                addm_wd = '/usr/tideway/TKU/Tpl_DEV'
        elif environment_condition == 'customer_tku':
            addm_wd = '/usr/tideway/TKU/Tpl_DEV'
            log.debug("This is a customer mode, files will be uploaded to hardcoded path: "+str(addm_wd))

        return addm_wd, test_path

    def pattern_path_cond(self, addm_vm_condition, **logical_conditions):
        """
        NOTE: addm_vm_condition - shoulbe be only in sep arg with ability to input None in var.

        Based on operational conditions - decide which path to use for patterns zip and upload \ activate

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
                local
                 - D:\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                 - D:\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

                remote(mirror)
                - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/tpl<version>/PatternName.zip
                - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/imports/tpl<version>/PatternName.zip
            if not dev_vm:
                local
                 - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                 - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

                remote(not DEV) - /usr/tideway/TKU/Tpl_DEV/PatternName.zip

        addm_vm_condition: str
        addm_zip_f - closure functions of zipping patterns
        addm_zip - path to zip in addm FS if available
        local_zip - path to zip in local FS
        :return: addm_zip_f, addm_zip, local_zip
        """
        # Assign
        path_to_result = ''
        zip_mirror     = ''
        addm_zip_f     = ''
        addm_zip       = ''
        local_zip      = ''

        assert isinstance(logical_conditions, dict)
        # Set examples in __init__ docstrings:
        import_conditions     = logical_conditions['import_conditions']

        addm_working_dir      = logical_conditions['addm_working_dir']
        local_conditions      = logical_conditions['local_conditions']
        environment_condition = local_conditions['environment_condition']

        # Make addm dev vm check to false for condition when this is customer mode.
        if environment_condition == 'customer_tku':
            addm_vm_condition = False

        assert isinstance(local_conditions, dict)
        # Based on imports mode:

        if import_conditions:
            log.debug("Making zip from imported patterns.")

            # Include 'imports' dir into the path:
            imports_dir = os.sep+"imports"+os.sep

            # Path of active pattern folder + imports dir + tpl<version dir>(or not is customer):
            # In dev mode I have pattern folder as name and result path to tpl after Preproc:
            if environment_condition == 'developer_tplpre':
                path_to_result = self.full_path_args['working_dir']+imports_dir+self.tpl_folder+os.sep

            # In customer mode I have just only imports folder and pattern name for module naming:
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
                # local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                local_zip = path_to_result+self.full_path_args['file_name'] + '.zip'
                log.debug("local_zip: "+str(local_zip))
            else:
                # I do not use this, because I want to zip files without uploading:
                addm_result_folder = addm_working_dir
                # Just make zip on local files and don't move it:
                # local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                local_zip = path_to_result+self.full_path_args['file_name'] + '.zip'
                log.debug("local_zip: "+str(local_zip))

            # In dev - use path_to_result with working dir and <tpl_ver> in it:
            if environment_condition == 'developer_tplpre':
                addm_zip_f = self.make_zip(path_to_result=path_to_result,
                                           active_folder=local_conditions['file_name'])
                # Making function obj for ZIP
                zip_mirror = addm_result_folder+"/"+self.full_path_args['file_name'] + '.zip'

            # In dev - use path_to_result with only working dir in it:
            elif environment_condition == 'customer_tku':
                addm_zip_f = self.make_zip(path_to_result=path_to_result,
                                           active_folder=local_conditions['file_name'])
                # Rewrite addm zip path to hardcoded:
                zip_mirror = addm_working_dir + "/" + local_conditions['file_name'] + '.zip'
                addm_result_folder = 'Ignore HGFS on customer mode.'

            # Path to zip with import included:
            # path_to_zip: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName/imports/tpl113/PatternName.zip
            addm_zip = zip_mirror

            log.debug("addm_zip: "+str(addm_zip))
            log.debug("addm_result_folder: "+str(addm_result_folder))
            log.debug("path_to_result: "+str(path_to_result))

        else:
            log.debug("Imports condition - NOT DEV IMPORTS to addm: Making zip with one active file.")

            # Path of active pattern to ZIP:
            # Path of active pattern folder + imports dir + tpl<version dir>(or not is customer):
            # In dev mode I have pattern folder as name and result path to tpl after Preproc:
            if environment_condition == 'developer_tplpre':
                path_to_result = self.full_path_args['working_dir']+os.sep+self.tpl_folder+os.sep
                path_to_file = path_to_result + os.sep + self.full_path_args['file_name']

            # In customer mode I have just only imports folder and pattern name for module naming:
            elif environment_condition == 'customer_tku':
                path_to_result = self.full_path_args['working_dir']+os.sep
                path_to_file = path_to_result + self.full_path_args['file_name']

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
                local_zip = path_to_result+self.full_path_args['file_name'] + '.zip'
                log.debug("local_zip: "+str(local_zip))
            else:
                # I don not use this, because I want to zip files without uploading:
                addm_result_folder = addm_working_dir
                # Just make zip on local files and don't move it:
                local_zip = path_to_result+self.full_path_args['file_name'] + '.zip'
                log.debug("local_zip: "+str(local_zip))

            # Making function obj for ZIP
            zip_remote = addm_result_folder+"/"+self.full_path_args['file_name']+ '.zip'

            addm_zip_f = self.make_zip(path_to_result=path_to_file,
                                       active_folder=self.full_path_args['file_name'],
                                       mode_single="Yes")

            # Path to zip with single pattern included:
            # addm_zip: /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternName/tpl113/PatternName.zip
            addm_zip = zip_remote

            log.debug("addm_zip: "+str(addm_zip))
            log.debug("addm_result_folder: "+str(addm_result_folder))
            log.debug("path_to_result: "+str(path_to_result))

        log.info("Module local zip path: "+str(local_zip))
        return addm_zip_f, addm_zip, local_zip

    def zip_activ_cond(self, **zipping_conditions):
        """
        Based on ADDM state - if DEV_VM or not - choose folder where activate or upload and activate ZIP with patterns.
        In case of customer run - addm dev option will be ignored.

        if dev_vm:
            local
            - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
            - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

            remote(mirror)
             - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/tpl<version>/PatternName.zip
             - /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/PatternFolder/imports/tpl<version>/PatternName.zip
        if not dev_vm:
            local
            - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
            - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

            remote
            - /usr/tideway/TKU/Tpl_DEV/PatternName.zip

        upload_f - closure function with zip upload to ADDM
        addm_activate_f - closure function with pattern activation in ADDM (False if upload only mode)
        :param zipping_conditions: set
        :return: upload_f, addm_activate_f
        """

        assert isinstance(zipping_conditions, dict)
        # Set examples in __init__ docstrings:
        addm_conditions   = zipping_conditions['addm_conditions']
        addm_zip          = zipping_conditions['addm_zip']
        local_zip         = zipping_conditions['local_zip']
        local_conditions  = zipping_conditions['local_conditions']

        assert isinstance(local_conditions, dict)
        pattern_file_name = local_conditions['file_name']
        pattern_folder    = local_conditions['pattern_folder']

        assert isinstance(addm_conditions, dict)
        addm_vm_condition = addm_conditions['dev_vm_check']
        # From args, of not set - use default system\system
        system_user           = addm_conditions['system_user']
        system_password       = addm_conditions['system_password']
        environment_condition = local_conditions['environment_condition']

        if environment_condition == 'developer_tplpre':
            if addm_vm_condition:
                # Just activate zip in mirrored path:
                log.info("Activating in mirrored filesystem.")
                addm_activate_f = self.make_activate_zip(zip_path        = addm_zip,
                                                         module_name     = pattern_folder,
                                                         system_user     = system_user,
                                                         system_password = system_password)
                upload_f = False

                return upload_f, addm_activate_f

            elif not addm_vm_condition:
                # Upload zip to addm custom folder and then activate:
                log.info("Uploading: "+str(addm_zip))

                # UPLOAD zip to ADDM via SFTP:
                upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)

                log.info("Activating: "+str(addm_zip))
                addm_activate_f = self.make_activate_zip(zip_path        = addm_zip,
                                                         module_name     = pattern_folder,
                                                         system_user     = system_user,
                                                         system_password = system_password)
                return upload_f, addm_activate_f

        elif environment_condition == 'customer_tku':
            log.info("Uploading: '/usr/tideway/TKU/Tpl_DEV/'")

            # UPLOAD zip to ADDM via SFTP:
            upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)

            log.info("Activating: "+str(addm_zip))
            addm_activate_f = self.make_activate_zip(zip_path        = addm_zip,
                                                     module_name     = pattern_file_name,
                                                     system_user     = system_user,
                                                     system_password = system_password)

            return upload_f, addm_activate_f

    def test_run_cond(self, test_conditions, addm_conditions, environment_condition):
        """
        Placeholder

        [{'test_wd': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\MSSQLServer\\tests',
        'rem_test_path': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/MSSQLServer/tests/test.py',
        'rem_test_wd': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/MSSQLServer/tests',
        'test_path': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\MSSQLServer\\tests\\test.py',
        'pattern': 'MicrosoftSQLServer.tplpre'}]


        :param test_conditions:
        :return: function from make_test_run
        """

        # Lets declare here some variables to see what we have:
        local_tests_path = self.full_path_args['pattern_test_t']
        active_pattern = self.full_path_args['file_name']+'.'+self.full_path_args['file_ext']

        workspace = self.full_path_args['workspace']
        addm_wd = addm_conditions['dev_vm_path']
        test_wd = self.working_dir+os.sep+'tests'


        # TODO: Check if related test run also an initial test? Do we need it run, or better leave in separate modes?
        if test_conditions['run_test']:
            log.debug("Will run single test for active pattern: "+str(local_tests_path))

            if local_tests_path and os.path.exists(local_tests_path):

                remote_test_wd = test_wd.replace(workspace, addm_wd).replace('\\', '/')
                remote_test_file = remote_test_wd+'/test.py'

                related_tests = []
                current_pattern_dict = dict(pattern       = active_pattern,
                                            test_path     = local_tests_path,
                                            rem_test_path = remote_test_file,
                                            test_wd       = test_wd,
                                            rem_test_wd   = remote_test_wd
                                            )
                related_tests.append(current_pattern_dict)
                # print(related_tests)

                if related_tests:
                    test_executor_f = self.make_test_run(tests_list=related_tests,
                                                         test_conditions=test_conditions)
                # log.debug("Test file path to run: "+str(remote_tests_path))

                    return test_executor_f

        elif test_conditions['related_tests']:
            log.debug("Will run related tests where active pattern is used: "+str(self.full_path_args['file_name']))

            related_tests = LocalLogic.get_related_tests(local_conditions=self.full_path_args,
                                                         dev_vm_path=addm_wd)
            # print(related_tests)
            test_executor_f = self.make_test_run(tests_list=related_tests,
                                                 test_conditions=test_conditions)

            return test_executor_f

# Functions to create closures for all related options:

    def make_test_read_query(self):
        """
        Closure for reading test.py queries.
        :return: func with query results list.
        """

        def test_queries():
            test_read = TestRead()
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

        def importer():
            tpl_imports = TPLimports(self.full_path_args)
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

        def pre_processing():
            preproc = Preproc()
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

        def syntax_check():
            syntax = SyntaxCheck()
            if_check = syntax.syntax_check(working_dir, disco_ver)
            return if_check

        return syntax_check

    def make_zip(self, path_to_result, active_folder, mode_single=None):
        """
        Closure for zipper function.
        Make zip for local folder!
        :type active_folder: str - folder where pattern lies and ready to zip
        :type path_to_result: str - path to zip with patterns
        :return: func zipper
        """

        def zipper():
            local_logic = LocalLogic()
            # Zip local processed files and return path to zip on local and name if zip for addm mirror FS:
            local_logic.make_zip(path_to_result, active_folder, mode_single)

        return zipper

    def make_tku_wiping(self, system_user, system_password):
        def wipe_tku():
            addm = AddmOperations(self.ssh)
            # Totally wipe knowledge update with tw_pattern_management --remove-all --force.
            addm.wipe_tku(system_user=system_user, system_password=system_password)

        return wipe_tku

    def make_upload_remote(self, zip_on_local, zip_on_remote):
        """
        Closure for pattern upload on remote addm via SFTP.
        :type zip_on_remote: str possible path to remote zip file
        :type zip_on_local: str actual path to local zip file
        :return: activate patterns func
        """

        def activate():
            addm = AddmOperations(self.ssh)
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

        def activate():
            addm = AddmOperations(self.ssh)
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

        :param addm_conditions: str
        :type module_name: str
        :return: func
        """

        disco_mode      = addm_conditions['disco_mode']
        host_list       = addm_conditions['scan_hosts']
        system_user     = addm_conditions['system_user']
        system_password = addm_conditions['system_password']

        def scan():
            addm_scan = AddmScan(self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm_scan.addm_scan(disco_mode,
                                host_list,
                                system_user,
                                system_password,
                                module_name)

        return scan

    def make_test_run(self, tests_list, test_conditions):
        """
        Closure placeholder for tests run
        :param tests_list: list
        :return:
        """
        def test_run():
            addm = AddmOperations(self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm.tests_executor(tests_list, test_conditions)

        return test_run


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message