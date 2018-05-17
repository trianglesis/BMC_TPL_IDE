"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import os
from check_ide.parse_args import ArgsParse
from check_ide.preproc import Preproc
from check_ide.imports import TPLimports
from check_ide.test_queries import TestRead
from check_ide.upload import AddmOperations
from check_ide.syntax_checker import SyntaxCheck
from check_ide.local_logic import LocalLogic
from check_ide.scan import AddmScan
# import json
# from pprint import pformat

import logging
log = logging.getLogger("check_ide.logger")


class GlobalLogic:

    def __init__(self, extra_args, known_args):
        """
        Initialize with options for logical operations.
        Check arg sets and output messages for different option scenarios.

        :return: func
        """
        # print(extra_args)
        # print(type(known_args))
        # print(known_args)

        # FULL PATH ARGS:
        self.tku_patterns_t    = ''
        self.workspace         = ''
        self.full_path         = ''
        self.working_dir       = ''
        self.patt_file_name    = ''
        self.patt_folder_name  = ''
        self.env_cond          = ''

        # ADDM ARGS:
        self.ssh             = ''
        self.tpl_folder      = ''
        self.scan_hosts      = ''
        self.dev_vm_check    = ''
        self.tpl_vers        = ''
        self.addm_prod       = ''
        self.disco_mode      = ''
        self.addm_ver        = ''
        self.dev_vm_path     = ''
        self.system_user     = ''
        self.system_password = ''

        # IMPORTS ARGS:
        self.recursive_imports = ''
        self.usual_imports     = ''
        self.read_test         = ''

        # TESTS ARGS:
        self.related_tests     = ''
        self.run_test          = ''

        # TKU OPER ARGS:
        self.wipe_tku          = ''

        # Get all available arguments in three sets based on its type:
        self.full_path_args, self.oper_args, self.addm_args_set = self.check_args_set(known_args=known_args,
                                                                                      extra_args=extra_args)

        # Check args in init module to further assign on function bodies:
        # FULL PATH ARGS:
        if isinstance(self.full_path_args, dict):
            '''
            Examples of arg sets
                
            PATH ARGS:

            CUSTOMER_MODE: 

            TKU_ZIP = "Technology-Knowledge-Update-2017-07-1-ADDM-11.1+"
                {
                    "BLADE_ENCLOSURE_t": "D:\\TKU\\TKU_ZIP\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+",
                    "SYSTEM_t": "D:\\TKU\\TKU_ZIP\\TKU-System-2017-07-1-ADDM-11.1+",
                    "tkn_main_t": "",
                    "tku_patterns_t": "",
                    "MIDDLEWAREDETAILS_t": "D:\\TKU\\TKU_ZIP\\TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+",
                    "workspace": "D:\\TKU",
                    "file_name": "PatternName",
                    "CLOUD_t": "",
                    "full_path": "D:\\TKU\\TKU_ZIP\\TKU-Core-2017-07-1-ADDM-11.1+\\PatternName.tpl",
                    "DBDETAILS_t": "D:\\TKU\\TKU_ZIP\\TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+",
                    "working_dir": "D:\\TKU\\TKU_ZIP\\TKU-Core-2017-07-1-ADDM-11.1+",
                    "CORE_t": "D:\\TKU\\TKU_ZIP\\TKU-Core-2017-07-1-ADDM-11.1+",
                    "file_ext": "tpl",
                    "pattern_folder": "TKU-Core-2017-07-1-ADDM-11.1+",
                    "MANAGEMENT_CONTROLLERS_t": "D:\\TKU\\TKU_ZIP\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+",
                    "STORAGE_t": "",
                    "buildscripts_t": "",
                    "self.env_cond": "customer_tku",
                    "LOAD_BALANCER_t": "D:\\TKU\\TKU_ZIP\\TKU-LoadBalancer-2017-07-1-ADDM-11.1+",
                    "tkn_sandbox_t": ""
                }

            TKU_DEVELOPER_MODE:                
            PATH ARGS:
                {
                    "MANAGEMENT_CONTROLLERS_t": "d:\\to_patterns\\MANAGEMENT_CONTROLLERS",
                    "CLOUD_t": "d:\\to_patterns\\CLOUD",
                    "BLADE_ENCLOSURE_t": "d:\\to_patterns\\BLADE_ENCLOSURE",
                    "file_name": "BMCRemedyARSystem",
                    "tkn_sandbox_t": "d:\\perforce\\addm\\tkn_sandbox",
                    "tku_patterns_t": "d:\\to_patterns",
                    "LOAD_BALANCER_t": "d:\\to_patterns\\LOAD_BALANCER",
                    "CORE_t": "d:\\to_patterns\\CORE",
                    "SYSTEM_t": "d:\\to_patterns\\SYSTEM",
                    "STORAGE_t": "d:\\to_patterns\\STORAGE",
                    "working_dir": "d:\\to_patterns\\CORE\\BMCRemedyARSystem",
                    "DBDETAILS_t": "d:\\to_patterns\\DBDETAILS",
                    "pattern_folder": "BMCRemedyARSystem",
                    "file_ext": "tplpre",
                    "self.env_cond": "developer_tplpre",
                    "tkn_main_t": "d:\\perforce\\addm\\tkn_main",
                    "pattern_test_t": "d:\\to_patterns\\CORE\\BMCRemedyARSystem\\tests\\test.py",
                    "buildscripts_t": "d:\\perforce\\addm\\tkn_main\\buildscripts",
                    "full_path": "d:\\to_patterns\\CORE\\BMCRemedyARSystem\\BMCRemedyARSystem.tplpre",
                    "workspace": "d:\\perforce",
                    "MIDDLEWAREDETAILS_t": "d:\\to_patterns\\MIDDLEWAREDETAILS"
                }

            '''

            # log.debug("Full path args OK.")
            # print(json.dumps(self.full_path_args, indent=4, ensure_ascii=False, default=pformat))

            # Assign most re-usable arguments here:
            self.tku_patterns_t   = self.full_path_args['tku_patterns_t']
            self.workspace        = self.full_path_args['workspace']
            self.full_path        = self.full_path_args['full_path']
            self.working_dir      = self.full_path_args['working_dir']
            self.patt_file_name   = self.full_path_args['file_name']
            self.patt_folder_name = self.full_path_args['pattern_folder']
            self.env_cond         = self.full_path_args['env_cond']

            if not self.working_dir:
                log.error("File working dir is not extracted - I cannot proceed any function.")
                msg = "There is no -full_path argument set or it cannot be parsed."
                raise AttributeError(msg)
        else:
            log.critical("No full path arguments were set. I can do nothing with this.")
            msg = "There is no -full_path argument set or it cannot be parsed."
            raise AttributeError(msg)

        # ADDM ARGS:
        if isinstance(self.addm_args_set, dict):
            if self.addm_args_set['ssh_connection']:
                '''
                    ADDM VM ARGS: 
                    {
                        "tpl_folder": "tpl113",
                        "scan_hosts": "0.0.0.0, 1.1.1.1",
                        "dev_vm_check": true,
                        "tpl_vers": "1.13",
                        "addm_prod": "Bobblehat",
                        "ssh_connection": "<paramiko.client.SSHClient object at 0x00000000036A0F98>",
                        "disco_mode": "record",
                        "addm_ver": "11.1",
                        "system_password": "system",
                        "dev_vm_path": "/usr/tideway/TKU",
                        "system_user": "system"
                    }
                '''

                # log.debug("ADDM args OK.")
                # print(json.dumps(self.addm_args_set, indent=4, ensure_ascii=False, default=pformat))

                # Assign most re-usable arguments here:
                self.ssh             = self.addm_args_set['ssh_connection']
                self.tpl_folder      = self.addm_args_set['tpl_folder']
                self.tpl_vers        = self.addm_args_set['tpl_vers']
                self.scan_hosts      = self.addm_args_set['scan_hosts']
                self.addm_prod       = self.addm_args_set['addm_prod']
                self.disco_mode      = self.addm_args_set['disco_mode']
                self.system_user     = self.addm_args_set['system_user']
                self.system_password = self.addm_args_set['system_password']
                self.addm_ver        = self.addm_args_set['addm_ver']
                self.dev_vm_path     = self.addm_args_set['dev_vm_path']
                self.dev_vm_check    = self.addm_args_set['dev_vm_check']

                log.debug("ADDM is active, args on place.")
            else:
                log.debug("ADDM is not active, no SSH.")
        else:
            log.debug("ADDM arguments wasn't set. Local run.")

        # Check operational args set:
        # IMPORTS CONDITIONS:
        # TESTS CONDITIONS:
        # TKU OPERATIONS:
        if isinstance(self.oper_args, dict):
            '''
                Operational args include current arg flags for any programm mode.
                In can include any new mode flag as dict or dict key with boolean val.
                
                {
                  "tests": {
                      "related_tests": false,
                      "test_failfast": false,
                      "run_test": false,
                      "test_verbose": false
                  },
                  "imports": {
                      "recursive_imports": false,
                      "usual_imports": false,
                      "read_test": false
                  },
                  "tku_oper": {
                      "wipe_tku": false
                  }
                }
                
            '''

            # log.debug("Operational args OK.")
            # print(json.dumps(self.oper_args, indent=4, ensure_ascii=False, default=pformat))

            # IMPORTS:
            if self.oper_args['imports']:
                '''
                    Set of args dedicated for imports logic.
                    WIll check_ide mode here and compose boolean logic.
                '''
                imports = self.oper_args['imports']

                # Assign most re-usable arguments here:
                self.recursive_imports = imports['recursive_imports']
                self.usual_imports     = imports['usual_imports']
                self.read_test         = imports['read_test']

                if not (self.usual_imports or self.recursive_imports) and not self.read_test:
                    self.import_cond = False
                else:
                    self.import_cond = imports

            else:
                self.import_cond = False
                log.debug("Import arguments was not set: "+str(self.oper_args['imports']))

            # TESTS:
            if self.oper_args['tests']:
                '''
                    Set of args dedicated for test execution logic.
                    WIll check_ide mode here and compose boolean logic.
                '''
                tests = self.oper_args['tests']

                # Assign most re-usable arguments here:
                self.related_tests     = tests['related_tests']
                self.run_test          = tests['run_test']

                if not (self.run_test or self.related_tests):
                    self.tst_cond = False
                else:
                    self.tst_cond = tests

            else:
                log.debug("No test runs.")
                self.tst_cond = False

            # TKU OPERATIONS:
            if self.oper_args['tku_oper']:
                '''
                    Set of args dedicated for ADDM management execution logic.
                    WIll check_ide mode here and compose boolean logic.
                '''
                tku_oper = self.oper_args['tku_oper']

                # Assign most re-usable arguments here:
                self.wipe_tku = tku_oper['wipe_tku']

            else:
                log.debug("No test runs.")
                self.tku_oper = False

        else:
            log.warning("There is no operational args found in arg dicts!")

    @staticmethod
    def check_args_set(**args_from_cmd):
        """
        This will check_ide args set in input.
        Based on set of args - it will compose another set of functions.
        The set of functions will consist of all needed functions on order to execute.

        Example:
            - for usual way for tplpre with imports and pack of patterns:
                -- 1. Imports_(for all from current pattern + all recursive patterns),
                   2. TPLPreproc_(for all in imports folder),
                   3. SyntaxCheck_(for all in imports folder), -- This probably will be removed later with AST
                   4. AskADDM_(ADDM SSH connection - check_ide supported tpl, working folder, save SSH session)
                   5. UploadPatterns_ (zip patterns for correspond tpl ver from ADDM - upload-activate)
                   6. StartScan_(start Discovery with options)
                   7. CheckScan_(Check when scan is finished and successful)
                   8. RunQuery_(Run Search SoftwareInstance or so and output result)
                   9. SaveResults_(save model file for SI and Query file for queries with results)
                   10. ...
            - for tpl usage (without Preproc or Syntax):
                -- 1. AskADDM_(ADDM SSH connection - check_ide supported tpl, working folder, save SSH session)
                   2. UploadPatterns_ (zip patterns for correspond tpl ver from ADDM - upload-activate)
                   3. StartScan_(start Discovery with options)
                   4. CheckScan_(Check when scan is finished and successful)
                   5. RunQuery_(Run Search SoftwareInstance or so and output result)
                   6. SaveResults_(save model file for SI and Query file for queries with results)
                   7. ...
            - for test.py (or something like that) if will be added:
                -- 1. AskADDM_(ADDM SSH connection - check_ide supported tpl, working folder, save SSH session)
                   2. StartTH_(start TestHarness in tku_patterns folder and output results)
                   3. ExecuteTest_(run test with set of options you send)
                   4. ValidateTests_(check_ide something you need to)
                   5. This section not even planned yet, can be changed.

        :param args_from_cmd: set
        :return:
        """
        parse_args = ArgsParse()

        return parse_args.gather_args(known_args=args_from_cmd['known_args'],
                                      extra_args=args_from_cmd['extra_args'])

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
            "addm_zip": "/usr/tideway/TKU/to_patterns/CORE/PatternName/imports/tpl113/PatternName.zip",
            "addm_working_dir": "/usr/tideway/TKU/to_patterns/CORE/PatternName",
            "local_zip": "ADDM is in DEV mode - not need to point to local zip file."
        }

        :rtype: object
        :return: pair of function sets with conditional functions to execute and result to debug.
        """

        conditional_functions, conditional_results = self.cond_args()

        return conditional_functions, conditional_results

# Doing business based on all decisions made:
    def cond_args(self):
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

        # Set operational option for dev or customer:
        log.debug("Program is operating in: '"+str(self.env_cond)+"' mode.")

        if self.scan_hosts and self.disco_mode and self.ssh \
                and not isinstance(self.tst_cond, dict):

            log.debug("ADDM discovery scan,")
            upload_scan = True

        elif not self.disco_mode and not self.scan_hosts and self.tpl_folder and self.ssh \
                and not isinstance(self.tst_cond, dict):

            log.debug("ADDM local processing.")
            local_proceed_for_addm = True

        elif not self.scan_hosts and self.tpl_folder and self.disco_mode and self.ssh \
                and not isinstance(self.tst_cond, dict):

            log.debug("ADDM Upload.")
            upload_only = True

        elif not self.ssh \
                and not isinstance(self.tst_cond, dict):

            log.debug("NO ADDM, local processing.")
            import_preproc_syntax_local = True

        elif self.ssh and isinstance(self.tst_cond, dict):

            tests_run = True
            log.debug("ADDM run tests.")
        # I don't know:
        else:
            conditional_debug = dict(
                tpl_folder = self.tpl_folder,
                scan_hosts = self.scan_hosts,
                disco_mode = self.disco_mode,
                ssh = self.ssh,
                tst_cond = self.tst_cond,
            )
            log.info("This set of conditional arguments is not supported by my logic, Please read docs.")
            log.debug("Conditional statuses: %s", conditional_debug)

        if upload_scan:
            '''
                When I have no args for scan AND NO args for ADDM disco,
                but have arg for tpl_vers - proceed files locally with that version.
                
                - Import patterns if needed on mode set in import_cond
                - Run preproc on patterns based on conditional arguments:
                - Run syntax check_ide based on cond args:
                - Generate addm working dir based on DEV condition:
                - Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
                - If you want to wipe all TKU before:
                - Using path to zip result from above - activate it in ADDM
                - Start scan action:
                - Better to use filename as active file - which initiates this run:
                
            '''
            log.info("ADDM Scan action.")
            log.debug("Operational mode: upload_scan")

            imports_f = self.imports_cond()
            preproc_f = self.preproc_cond()
            syntax_check_f = self.syntax_cond(tpl_version = self.addm_ver)
            addm_working_dir, tests_path = self.addm_dev_cond()

            zip_files_f, addm_zip, local_zip = self.pattern_path_cond(addm_working_dir=addm_working_dir)

            # WIPE TKU:
            if self.wipe_tku:
                wipe_tku_f = self.make_tku_wiping(system_user=self.system_user,
                                                  system_password=self.system_password)

            upload_f, addm_activate_f = self.zip_activ_cond(addm_zip  = addm_zip,
                                                            local_zip = local_zip)

            scan_f = self.make_scan(module_name = self.full_path_args['file_name'])

        elif local_proceed_for_addm:
            """
                When there is an active SSH connection to ADDM but no scan and host list options -
                Make version check_ide and zip patterns for current ADDM version.
                
                - Import patterns if needed on mode set in import_cond
                - Run preproc on patterns based on conditional arguments:
                - Run syntax check_ide based on cond args:
                - Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
                - tpl_vers addm_prod addm_ver
                
            """
            log.info("No ADDM action. Local processing")
            log.debug("Operational mode: local_proceed_for_addm")

            imports_f = self.imports_cond()
            preproc_f = self.preproc_cond()
            syntax_check_f = self.syntax_cond(tpl_version = self.addm_ver)
            zip_files_f, addm_zip, local_zip = self.pattern_path_cond(addm_working_dir  = 'Null')

            log.info("Zipped for ADDM: "+str(self.addm_prod) +
                     " Ver. "+str(self.addm_ver) +
                     " Tpl v. "+str(self.tpl_vers))

        elif upload_only:
            """ 
                When I have NO args for Scan, 
                but have args for ADDM status and disco - will start upload only.
                
                - Import patterns if needed on mode set in import_cond
                - Run preproc on patterns based on conditional arguments:
                - Run syntax check_ide based on cond args:
                - Generate addm working dir based on DEV condition:
                - Zipping files in working dir and compose possible path to this zip in ADDM to upload or activate.
                - If you want to wipe all TKU before:
                - Using path to zip result from above - activate it in ADDM
                - No Scan action because: not self.scan_hosts just upload and activate.
                 
            """
            log.info("ADDM Upload. No scan.")
            log.debug("Operational mode: upload_only")

            imports_f = self.imports_cond()
            preproc_f = self.preproc_cond()
            syntax_check_f = self.syntax_cond(tpl_version = self.addm_ver)
            addm_working_dir, tests_path = self.addm_dev_cond()

            zip_files_f, addm_zip, local_zip = self.pattern_path_cond(addm_working_dir=addm_working_dir)

            if self.wipe_tku:
                wipe_tku_f = self.make_tku_wiping(system_user=self.system_user,
                                                  system_password=self.system_password)

            upload_f, addm_activate_f = self.zip_activ_cond(addm_zip        = addm_zip,
                                                            local_zip       = local_zip)

            log.info("Zipped for ADDM: "+str(self.addm_prod) +
                     " Ver. "+str(self.addm_ver) +
                     " Tpl v. "+str(self.tpl_vers))

        elif import_preproc_syntax_local:
            """
            I have no active connection to ADDM so I don't know about tpl version to generate and zip
            - SO I will just import, Preproc and check_ide syntax
            
            - Import patterns if needed on mode set in import_cond
            - Run preproc on patterns based on conditional arguments:
            
            - Run syntax check_ide based on cond args:
            - Maybe I can add tpl_version for offline checks but what for?
            """
            log.info("Local processing, no ADDM connection.")
            log.debug("Operational mode: import_preproc_syntax_local")

            imports_f = self.imports_cond()
            preproc_f = self.preproc_cond()
            syntax_check_f = self.syntax_cond(tpl_version = '')

            _local_mode_ = 'There is no ADDM connection, program is running in local mode.'
            addm_zip         = _local_mode_
            local_zip        = _local_mode_
            addm_working_dir = _local_mode_

        # When ADDM connection is present and test options used:
        elif tests_run:
            log.info("Run tests for current pattern.")
            log.debug("ADDM connection is present and test options used.")
            test_executor_f = self.test_run_cond()

        # I don't know:
        else:
            log.warning("I can't understand the logic of current set of options. More in debug.")

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
    def imports_cond(self):
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

        """

        import_cond_dict = dict(parse_tests_patterns=False,
                                parse_tests_queries=False,
                                import_patterns=False)

        if isinstance(self.import_cond, dict):

            if self.env_cond == 'developer_tplpre':
                log.debug("Running in 'developer_tplpre'.")

                # NORMAL IMPORTS
                if self.usual_imports:
                    log.info("No extra imports. TPLPreprocessor will import.")
                    return import_cond_dict

                # RECURSIVE MODE:
                elif self.recursive_imports and not self.read_test:
                    log.info("Recursive imports.")
                    imports_f = self.make_imports(extra_patterns = None)
                    import_cond_dict['import_patterns'] = imports_f

                    return import_cond_dict

                # TESTs + RECURSIVE MODE:
                elif self.read_test and self.recursive_imports:
                    """
                        - Read test.py and extract query for future validation after addm scan and save model:
                        - Later if -T in arg - use this, if no - just ignore.
                        - Read test.py and extract list of patterns from self.setupPatterns
                        - This is list of patterns I need to import from test.py.
                        - Import tplpre's in recursive mode with extras from test.py:
                    """
                    log.info("Run test+recursive imports mode.")
                    query_t = self.make_test_read_query()
                    imports_t = TestRead().import_pattern_tests(self.working_dir)
                    imports_f = self.make_imports(extra_patterns = imports_t)

                    import_cond_dict['parse_tests_queries'] = query_t
                    import_cond_dict['import_patterns'] = imports_f

                    return import_cond_dict

                # SOLO MODE:
                elif not (self.usual_imports or self.recursive_imports) and not self.read_test:
                    log.debug("There are no dev arguments found for Test read, "
                              "or imports, or recursive imports.")
                    log.info("Using as standalone pattern file tplpre.")

                    return import_cond_dict

                else:
                    log.debug("This 'import_cond' is not operable: "+str(self.import_cond))

            elif self.env_cond == 'developer_tpl':
                log.debug("Running in 'developer_tpl' mode. No imports, tests can be used here.")
                log.info("Using as standalone pattern file tpl.")

                return import_cond_dict

            elif self.env_cond == 'customer_tku':
                log.debug("Running in 'customer_tku'.")

                if self.recursive_imports:
                    log.info("Imports logic working in customer mode.")
                    # Import tplpre's in recursive mode:
                    imports_f = self.make_imports(extra_patterns   = None)

                    import_cond_dict['import_patterns'] = imports_f
                    return import_cond_dict

                else:
                    log.info("Working in customer mode, all other importing option will be ignored.")

            else:
                log.debug("This 'self.env_cond' is not operable: "+str(self.env_cond))
        else:
            log.debug("No import options passed.")

        return import_cond_dict

    def preproc_cond(self):
        """
        Based on conditional args - run Preproc with import folder
        after my own method, or usual preproc method or even solo pattern preproc.

        Ignore step in customer mode.
        """

        import_cond = self.import_cond

        if self.env_cond == 'developer_tplpre':

            # ANY IMPORT:
            if isinstance(import_cond, dict):

                # USUAL IMPORTS - TPLPreproc:
                if self.usual_imports and not self.recursive_imports and not self.read_test:

                    log.info("TPLPreprocessor run on pattern and import.")
                    log.debug("TPLPreprocessor will run on active file and import "
                              "by its own logic. (usual_imports)")
                    preproc_cond_f = self.make_preproc(workspace   = self.workspace,
                                                       input_path  = self.full_path,
                                                       output_path = self.working_dir,
                                                       mode        = "usual_imports")
                    return preproc_cond_f

                # MY IMPORTS TPLPreproc on 'imports':
                elif self.recursive_imports or self.read_test and not self.usual_imports:

                    log.info("TPLPreprocessor on imports.")
                    log.debug("TPLPreprocessor will run on imports folder after "
                              "my recursive importing logic. "
                              "(recursive_imports)")
                    # After R imports are finish its work - run TPLPreprocessor on it
                    preproc_cond_f = self.make_preproc(workspace   = self.workspace,
                                                       input_path  = self.working_dir+os.sep+"imports",
                                                       output_path = self.working_dir+os.sep+"imports",
                                                       mode        = "recursive_imports")
                    return preproc_cond_f

                # NOTHING:
                else:
                    log.debug("This 'import_cond' is not operable: "+str(import_cond))

            # SOLO mode:
            else:
                log.info("TPLPreprocessor run on pattern without imports.")
                log.debug("TPLPreprocessor will run on active file without "
                          "any additional imports. (solo_mode)")

                preproc_cond_f = self.make_preproc(workspace   = self.workspace,
                                                   input_path  = self.full_path,
                                                   output_path = self.working_dir,
                                                   mode        = "solo_mode")

                return preproc_cond_f

        # CUSTOMER IMPORT:
        elif self.env_cond == 'customer_tku':
            log.debug("Ignoring TPLPreprocessor on customer_tku environment execution. "
                      "All files should be tpl.")
            return False

        # NO IMPORT FOR TPL:
        elif self.env_cond == 'developer_tpl':
            log.debug("No imports for dev tpl.")
            return False

        # NOTHING:
        else:
            log.debug("This 'self.env_cond' is not operable: "+str(self.env_cond))

    def syntax_cond(self, tpl_version):
        """
        Run syntax with options based on conditional arguments.

        If ADDM did not return any version - syntax check_ide will run for all available versions.
        Optional: arg set of tpl version can be used here.

        By default - results printed in raw mode. Further execution continues.

        :param logical_conditions: set
        :return: func
        """

        # Set examples in __init__ docstrings:
        import_cond = self.import_cond

        syntax_check_cond_f = False

        # IMPORTS DICT:
        if isinstance(import_cond, dict):
            # Preproc on NORMAL IMPORTS
            if self.usual_imports:
                """
                    - If no addm version - 
                    it will use empty string as arg and run syntax check_ide for all supported versions.
                """
                log.info("Syntax check_ide TPLPreprocessor result.")
                log.debug("Syntax check_ide will run on tpl folders after usual TPLPreproc output. (usual_imports)")
                syntax_check_cond_f = self.make_syntax_check(self.working_dir, disco_ver=tpl_version)

            # Preproc will run on all files from folder 'imports'
            elif self.recursive_imports or self.read_test:
                """
                    - After TPLPreprocessor finished its work - run Syntax Check on folder imports
                    - If no addm version - 
                    it will use empty string as arg and run syntax check_ide for all supported versions.
                """
                log.info("Syntax check_ide on imports.")
                log.debug("Syntax check_ide will run on imports folder after my importing logic. "
                          "(recursive_imports or read_test)")
                syntax_check_cond_f = self.make_syntax_check(self.working_dir+os.sep+"imports", disco_ver=tpl_version)

            else:
                log.debug("This mode is not operational: "+str(self.import_cond))

        # SOLO RUNS:
        else:
            """
                - If no addm version - it will use empty string as arg and run syntax check_ide for all versions.
                - In this condition syntax check_ide will hope that imports are already in folder after previous runs.
            """
            if self.env_cond == 'developer_tplpre' or self.env_cond == 'developer_tpl':
                log.info("1/1 Syntax check_ide solo file.")
                log.debug("1/2 Imports was already created just checking syntax for active pattern. "
                          "(not read_test not recursive_imports not usual_imports)")
                syntax_check_cond_f = self.make_syntax_check(self.working_dir, disco_ver=tpl_version)

            elif self.env_cond == 'customer_tku':

                log.warning("TPLint cannot check_ide syntax for single tpl file!"
                            "On other way it will check_ide syntax for whole CORE "
                            "folder and this can take too much time."
                            "To check_ide syntax please choose usual imports option, "
                            "so TPLint will run it only for 'imports' folder!")

            else:
                log.debug("This mode is not operational: "+str(self.env_cond))

        return syntax_check_cond_f

    def addm_dev_cond(self):
        """
        Based on args - make decision is ADDM dev or not - and compose paths for DEV or not.

        """
        # Assign
        addm_wd = ''
        test_path = ''

        # Set examples in __init__ docstrings:
        if self.env_cond == 'developer_tplpre':
            if self.dev_vm_check:
                log.debug("DEV ADDM - files activating in mirrored filesystem.")
                # Compose paths:
                local_logic = LocalLogic()
                addm_wd, test_path = \
                    local_logic.addm_compose_paths(dev_vm_path    = self.dev_vm_path,
                                                   pattern_folder = self.full_path_args['pattern_folder'])
            elif not self.dev_vm_check:
                log.debug("Usual ADDM - files uploading: '/usr/tideway/TKU/Tpl_DEV/'")
                addm_wd = '/usr/tideway/TKU/Tpl_DEV'
            else:
                log.debug("This 'self.dev_vm_check' is not operable: "+str(self.dev_vm_check))
        elif self.env_cond == 'customer_tku':
            addm_wd = '/usr/tideway/TKU/Tpl_DEV'
            log.debug("This is a customer mode, files will be uploaded to hardcoded path: "+str(addm_wd))
        else:
            log.debug("This 'self.env_cond' is not operable: "+str(self.env_cond))

        return addm_wd, test_path

    def pattern_path_cond(self, addm_working_dir):
        """
        NOTE: addm_vm_condition - should be be only in sep arg with ability to input None in var.

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
                - /usr/tideway/TKU/to_patterns/CORE/PatternFolder/tpl<version>/PatternName.zip
                - /usr/tideway/TKU/to_patterns/CORE/PatternFolder/imports/tpl<version>/PatternName.zip
            if not dev_vm:
                local
                 - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\tpl<version>\PatternName.zip
                 - D:\folder\addm\tkn_main\tku_patterns\CORE\PatternFolder\imports\tpl<version>\PatternName.zip

                remote(not DEV) - /usr/tideway/TKU/Tpl_DEV/PatternName.zip

        addm_vm_condition: str
        :return: addm_zip_f, addm_zip, local_zip
        """

        # Assign
        path_to_result = ''
        zip_mirror     = ''
        addm_zip_f     = ''
        path_to_file   = ''

        # Make addm dev vm check_ide to false for condition when this is customer mode.
        if self.env_cond == 'customer_tku':
            addm_vm = False
        else:
            addm_vm = self.dev_vm_check

        local_arg   = self.full_path_args

        file_name   = local_arg['file_name']
        work_dir    = local_arg['working_dir']
        tpl         = self.tpl_folder
        env_cond    = self.env_cond
        _mirror_    = 'ADDM is in DEV mode - not need to point to local zip file.'
        imports_dir = os.sep+"imports"+os.sep

        import_cond = self.import_cond

        # IMPORTS DICT: self.import_cond = imports
        if isinstance(import_cond, dict):
            """
                - Include 'imports' dir into the path:
                - Path of active pattern folder + imports dir + tpl<version dir>(or not is customer):
                - In dev mode I have pattern folder as name and result path to tpl after Preproc:
                - In customer mode I have just only imports folder and pattern name for module naming:
            """
            log.debug("Making zip from imported patterns.")

            if env_cond == 'developer_tplpre':
                path_to_result = work_dir + imports_dir + tpl + os.sep

            elif env_cond == 'customer_tku':
                path_to_result = work_dir + imports_dir  # already os.sep

            else:
                log.debug("DEV STUB: This 'env_cond' is not operable: "+str(env_cond))

            if addm_vm:
                """
                    - Pattern remote path in ADDM FS:
                    - On DEV ADDM (example docs: remote(mirror)): /usr/tideway/TKU/to_patterns/...
                    - I do not need this, because on DEV VM I will just activate zip in mirror FS
                """
                addm_result_folder = addm_working_dir + "/imports/" + tpl
                local_zip = _mirror_

            elif not addm_vm:
                """
                    - Not on DEV ADDM (example docs: remote(not DEV)): /usr/tideway/TKU/Tpl_DEV/
                    - addm_result_folder: /usr/tideway/TKU/Tpl_DEV
                    - local_zip: d:\workspace\addm\tkn_main\tku_patterns\CORE\PatternName\imports\tpl113\PatternName.zip
                    - local_zip = path_to_result+self.full_path_args['pattern_folder'] + '.zip'
                """
                addm_result_folder = addm_working_dir
                local_zip          = path_to_result + file_name + '.zip'
            else:
                """
                    - I do not use this, because I want to zip files without uploading:
                    - Just make zip on local files and don't move it:
                    - local_zip = path_to_result+local_arg['pattern_folder'] + '.zip'
                """
                addm_result_folder = addm_working_dir
                local_zip          = path_to_result + file_name + '.zip'

            if env_cond == 'developer_tplpre':
                """
                    - In dev - use path_to_result with working dir and <tpl_ver> in it:
                    - Making function obj for ZIP
                """
                addm_zip_f = self.make_zip(path=path_to_result, module_name=file_name)
                zip_mirror = addm_result_folder + "/" + file_name + '.zip'

            elif env_cond == 'customer_tku':
                """
                    - In dev - use path_to_result with only working dir in it:
                    - Rewrite addm zip path to hardcoded:
                """
                addm_zip_f         = self.make_zip(path=path_to_result, module_name=file_name)
                zip_mirror         = addm_working_dir + "/" + file_name + '.zip'
                addm_result_folder = 'Ignore HGFS on customer mode.'
            else:
                log.debug("This 'env_cond' is not operable: "+str(env_cond))

            """
                - Path to zip with import included:
                - path_to_zip: /usr/tideway/TKU/to_patterns/CORE/PatternName/imports/tpl113/PatternName.zip
            """
            addm_zip = zip_mirror

        # IMPORTS DICT = False: self.import_cond = False
        else:
            """
                - Path of active pattern to ZIP:
                - Path of active pattern folder + imports dir + tpl<version dir>(or not is customer):
                - In dev mode I have pattern folder as name and result path to tpl after Preproc:
            """
            log.debug("Imports condition - NOT DEV IMPORTS to addm: Making zip with one active file.")

            # In customer mode I have just only imports folder and pattern name for module naming:
            if env_cond == 'developer_tplpre':
                path_to_result = work_dir + os.sep + tpl + os.sep
                path_to_file   = path_to_result + os.sep + file_name

            elif env_cond == 'customer_tku':
                path_to_result = work_dir + os.sep
                path_to_file   = path_to_result + file_name
            else:
                log.debug("This 'env_cond' is not operable: "+str(env_cond))

            if addm_vm:
                """
                    - Pattern remote path in ADDM FS:
                    - On DEV ADDM (example docs: remote(mirror)):
                    - addm_result_folder: /usr/tideway/TKU/to_patterns/CORE/PatternName/tpl113
                    - I do not need this, because on DEV VM I will just activate zip in mirror FS
                """
                addm_result_folder = addm_working_dir + "/" + tpl
                local_zip          = _mirror_

            elif not addm_vm:
                """
                    - Not on DEV ADDM (example docs: remote(not DEV)): /usr/tideway/TKU/Tpl_DEV/
                    - addm_result_folder: /usr/tideway/TKU/Tpl_DEV
                    - local_zip: d:\workspace\addm\tkn_main\tku_patterns\CORE\PatternName\tpl113\PatternName.zip
                """
                addm_result_folder = addm_working_dir
                local_zip          = path_to_result + file_name + '.zip'

            else:
                """
                    - I don not use this, because I want to zip files without uploading:
                    - Just make zip on local files and don't move it:
                """
                addm_result_folder = addm_working_dir
                local_zip          = path_to_result + file_name + '.zip'

            # Making function obj for ZIP
            zip_remote = addm_result_folder + "/" + file_name + '.zip'
            addm_zip_f = self.make_zip(path=path_to_file, module_name=file_name, mode_single="Yes")

            """
                - Path to zip with single pattern included:
                - addm_zip: /usr/tideway/TKU/to_patterns/CORE/PatternName/tpl113/PatternName.zip
            """
            addm_zip = zip_remote

        log.debug("addm_zip: "+str(addm_zip))
        log.debug("addm_result_folder: "+str(addm_result_folder))
        log.debug("path_to_result: "+str(path_to_result))
        log.debug("Module local zip path: "+str(local_zip))

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
             - /usr/tideway/TKU/to_patterns/CORE/PatternFolder/tpl<version>/PatternName.zip
             - /usr/tideway/TKU/to_patterns/CORE/PatternFolder/imports/tpl<version>/PatternName.zip
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

        # Set examples in __init__ docstrings:
        addm_zip    = zipping_conditions['addm_zip']
        local_zip   = zipping_conditions['local_zip']

        pattern_file_name = self.patt_file_name
        pattern_folder    = self.patt_folder_name

        # DEVELOPER OPTIONS:
        if self.env_cond == 'developer_tplpre':

            # HGFS SHARE:
            if self.dev_vm_check:
                # Just activate zip in mirrored path:
                log.info("Activating in mirrored filesystem.")
                addm_activate_f = self.make_activate_zip(zip_path = addm_zip, module_name = pattern_folder)
                upload_f = False
                return upload_f, addm_activate_f

            # NO SHARE:
            elif not self.dev_vm_check:
                # Upload zip to addm custom folder and then activate:
                log.info("Uploading: "+str(addm_zip))
                # UPLOAD zip to ADDM via SFTP:
                upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)
                log.info("Activating: "+str(addm_zip))
                addm_activate_f = self.make_activate_zip(zip_path = addm_zip, module_name = pattern_folder)
                return upload_f, addm_activate_f

            # FAIL:
            else:
                log.debug("This 'self.dev_vm_check' is not operable: "+str(self.dev_vm_check))

        # CUSTOMER ADDM NO SHARE
        elif self.env_cond == 'customer_tku':
            log.info("Uploading: '/usr/tideway/TKU/Tpl_DEV/'")

            # UPLOAD zip to ADDM via SFTP:
            upload_f = self.make_upload_remote(zip_on_local=local_zip, zip_on_remote=addm_zip)
            log.info("Activating: "+str(addm_zip))
            addm_activate_f = self.make_activate_zip(zip_path = addm_zip, module_name = pattern_file_name)

            return upload_f, addm_activate_f

        # DEVELOPER TPL
        elif self.env_cond == 'developer_tpl':
            pass
        else:
            log.debug("This 'self.env_cond' is not operable: "+str(self.env_cond))

    def test_run_cond(self):
        """
        This function gets self.tst_cond and check_ide if this is dict.
        Then it run different scenarios.

        [{
          'test_wd': 'D:\\to_patterns\\CORE\\MSSQLServer\\tests',
          'rem_test_path': '/usr/tideway/TKU/to_patterns/CORE/MSSQLServer/tests/test.py',
          'rem_test_wd': '/usr/tideway/TKU/to_patterns/CORE/MSSQLServer/tests',
          'test_path': 'D:\\to_patterns\\CORE\\MSSQLServer\\tests\\test.py',
          'pattern': 'MicrosoftSQLServer.tplpre'
        }]

        :return: function from make_test_run
        """
        tst_cond = self.tst_cond

        # Lets declare here some variables to see what we have:
        local_tests_path = self.full_path_args['pattern_test_t']
        active_pattern = self.full_path_args['file_name']+'.'+self.full_path_args['file_ext']
        test_wd = self.working_dir+os.sep+'tests'

        # TST_COND DICT:
        if isinstance(tst_cond, dict):

            # SINGLE TEST:
            if tst_cond['run_test']:
                log.debug("Will run single test for active pattern: "+str(local_tests_path))

                if local_tests_path and os.path.exists(local_tests_path):

                    # This should be a list with single test, but it use same exec as related tests.
                    related_tests = []
                    remote_test_wd = test_wd.replace(self.workspace, self.dev_vm_path).replace('\\', '/')
                    remote_test_file = remote_test_wd+'/test.py'

                    current_pattern_dict = dict(pattern       = active_pattern,
                                                test_path     = local_tests_path,
                                                rem_test_path = remote_test_file,
                                                test_wd       = test_wd,
                                                rem_test_wd   = remote_test_wd
                                                )
                    related_tests.append(current_pattern_dict)
                    # print(related_tests)

                    # This should be a list with single test, but it use same exec as related tests.
                    if related_tests:
                        test_executor_f = self.make_test_run(tests_list=related_tests,
                                                             tst_cond=tst_cond)
                    # log.debug("Test file path to run: "+str(remote_tests_path))
                        return test_executor_f
                else:
                    log.warning("Path is not exist: "+str(local_tests_path))

            # RELATED TESTS:
            elif tst_cond['related_tests']:
                log.debug("Will run related tests where active pattern is used: "+str(self.full_path_args['file_name']))

                path_logic = LocalLogic()
                related_tests = path_logic.get_related_tests(local_cond=self.full_path_args,
                                                             dev_vm_path=self.dev_vm_path)
                # print(related_tests)
                test_executor_f = self.make_test_run(tests_list=related_tests,
                                                     tst_cond=tst_cond)
                return test_executor_f

            # UNKNOWN:
            else:
                log.debug("This 'tst_cond' is not operable: "+str(tst_cond))

        # TST_COND = False
        else:
            log.debug("No test run, tst_cond = False.")


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

    def make_imports(self, extra_patterns):
        """
        Closure for imports function.
        Version for customer run.
        Based or arguments - decide which import will run.
        Or nothing to run at all.

        :return: func with imports
        """
        full_path_args = self.full_path_args

        def importer():
            tpl_imports = TPLimports(full_path_args)
            # Now I don't need args because class was initialized with args above:
            tpl_imports.import_modules(full_path_args=full_path_args,
                                       extra_patterns=extra_patterns)
        return importer

    @staticmethod
    def make_preproc(workspace, input_path, output_path, mode):
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

    @staticmethod
    def make_syntax_check(working_dir, disco_ver):
        """
        Closure for syntax check_ide function.

        Run LOCAL syntax check_ide procedure in selected folders or files.
        Can run ONLY when imports from patter are also in the same folder.
        Should be ignored in SOLO MODE.

        :param working_dir: str - input dir where run syntax check_ide
        :param disco_ver: str - version of discover engine to use for check_ide, if empty - run all.
        :return: func - syntax check_ide with args in it.
        """

        def syntax_check():
            syntax = SyntaxCheck()
            if_check = syntax.syntax_check(working_dir, disco_ver)
            return if_check

        return syntax_check

    @staticmethod
    def make_zip(path, module_name, mode_single=None):
        """
        Closure for zipper function.
        Make zip for local folder!
        :param mode_single:
        :type path: str - folder where pattern lies and ready to zip
        :type module_name: str - zip name
        :return: func zipper
        """

        def zipper():
            local_logic = LocalLogic()
            # Zip local processed files and return path to zip on local and name if zip for addm mirror FS:
            local_logic.make_zip(path, module_name, mode_single)

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
    
    def make_activate_zip(self, zip_path, module_name):
        """
        Closure for pattern activation.
        Input arg to zip path - can be local or remote.

        :type module_name: str
        :type zip_path: str
        :return: func
        """
        system_user = self.system_user
        system_password = self.system_password

        def activate():
            addm = AddmOperations(self.ssh)
            # Activate zip package using path from arg (local|remote):
            addm.activate_knowledge(zip_path, module_name, system_user, system_password)

        return activate
    
    def make_scan(self, module_name):
        """
        Closure for addm start scan function with args.

        :type module_name: str
        :return: func
        """

        disco_mode      = self.disco_mode
        host_list       = self.scan_hosts
        system_user     = self.system_user
        system_password = self.system_password

        def scan():
            addm_scan = AddmScan(self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm_scan.addm_scan(disco_mode,
                                host_list,
                                system_user,
                                system_password,
                                module_name)

        return scan

    def make_test_run(self, tests_list, tst_cond):
        """
        Closure placeholder for tests run
        :param tst_cond:
        :param tests_list: list
        :return:
        """
        def test_run():
            addm = AddmOperations(self.ssh)
            # Activate local zip package using remote mirror path to it:
            addm.tests_executor(tests_list, tst_cond)

        return test_run
