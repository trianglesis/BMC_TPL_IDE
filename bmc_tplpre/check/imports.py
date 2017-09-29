"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""


import re
import os
import shutil
import stat
import logging
from check.local_logic import LocalLogic
from operator import itemgetter

log = logging.getLogger("check.logger")


class TPLimports:

    def __init__(self, full_path_args):

        """
        Initialize with startup set of arguments.


        DEV:

            Step 1: List patterns in current folder of active pattern.
            Step 1.1 - Step 1.2: Read patterns from current folders and extract import modules and pattern modules.
                      Add import modules to list which will be used for finding in extra places.
                      Add pattern modules to list which will be used to
                      compare if we found and know this module already.
            Step 1.3: Use list of found import modules from read pattern (Step 1.2) and start searching in extra places.


            Round: 1 - of recursive searching patterns.

                Step 2:   Searching modules from each found pattern from Step 1.
                Step 2.1: Before execute search in read_pattern - make list of patterns
                from all folders from extra_folders.
                          Search in each pattern from list of patterns.
                Step 2.2: Add import modules to list which will be used for finding in extra places in next round.
                          Add pattern modules to list which will be used to compare if we found and
                          know this module already.
                Step 2:   in while execution:
                          Compare found module items with list of pattern modules which was already
                          found and remove it match.

            Round: 2 - of recursive searching patterns.
                Repeat execution with vars from Round 1

            Round: 3 - of recursive searching patterns.
                Repeat execution with vars from Round 2
                Break the loop 'while < 3'

            Step 3: Show list of modules which wasn't found anywhere during 3 rounds in log warning.
            Step 3.1: Show list of found modules and path to patterns in log debug.

            Step 4: Wiping 'imports' folder before add new imports in it.
                Step 4.1 If folder cannot be wiped - show warning log.

            Step 5: Create 'imports' folder if isn't exist.
            Step 5.1: Copy pattern to imports folder and show debug log with path to copied pattern.

        Customer:
            Same steps but with paths in TKU Update and tpl files.

            Example:
                conditions: {
                    "local_cond": {
                        "BLADE_ENCLOSURE_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-BladeEnclosure-2017-07-1-ADDM-11.1+",
                        "buildscripts_t": "",
                        "DBDETAILS_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+",
                        "tkn_sandbox_t": "",
                        "working_dir": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-Core-2017-07-1-ADDM-11.1+",
                        "LOAD_BALANCER_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-LoadBalancer-2017-07-1-ADDM-11.1+",
                        "CLOUD_t": "",
                        "STORAGE_t": "",
                        "pattern_folder": "TKU-Core-2017-07-1-ADDM-11.1+",
                        "env_cond": "customer_tku",
                        "SYSTEM_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-System-2017-07-1-ADDM-11.1+",
                        # "SupportingFiles_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-Core-2017-07-1-ADDM-11.1+",
                        "file_name": "BMCRemedyARSystem",
                        "MIDDLEWAREDETAILS_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+",
                        "file_ext": "tpl",
                        "tkn_main_t": "",
                        "full_path": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-Core-2017-07-1-ADDM-11.1+\\BMCRemedyARSystem.tpl",
                        "CORE_t": "D:\\custom_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                        TKU-Core-2017-07-1-ADDM-11.1+",
                        "MANAGEMENT_CONTROLLERS_t": "D:\\custom_path\\TKU\\
                        Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+",
                        "tku_patterns_t": "",
                        "workspace": "D:\\custom_path\\TKU"
                    }
                }


        :param full_path_args: args parsed and composed
        """

        self.full_path_args = full_path_args

        if self.full_path_args:
            self.workspace   = self.full_path_args['workspace']
            self.full_path   = self.full_path_args['full_path']
            self.working_dir = self.full_path_args['working_dir']
            self.file_ext    = self.full_path_args['file_ext']

            if not self.working_dir:
                log.error("File working dir is not extracted - I cannot proceed any function.")

            log.debug("Arguments from -full_path are obtained and program will make decisions.")
        else:
            log.warning("Arguments from -full_path are'n obtained and program cannot make decisions.")

        self.pattern_import_all_r = re.compile('from\s+(.+?)\s+import\s+\S+\s+\d+')
        self.pattern_module_name_r = re.compile('tpl\s+(?:\$\$TPLVERSION\$\$|\d+\.\d+)\s+module\s+(\S+);')

    def import_modules(self, full_path_args, extra_patterns):
        """
        Import modules.
        Based on conditional args it can import tpl for customer or tplre for dev.
        Get full paths to each extra folders from args.

        :param extra_patterns:
        :type full_path_args: dict

        """
        local_cond = full_path_args
        env_mode   = full_path_args['env_cond']

        log.debug("Step 1. Starting import functions. Read pattern: "+str(local_cond['file_name']))

        # Get extra folders from previous parse in full_path_args.
        local_logic = LocalLogic()
        extra_folders = local_logic.check_extra_folders(local_cond)

        current_modules_name = []  # Modules from KNOWN and FOUND and CURRENT.
        find_importing_modules = []  # Modules which I should found.
        # Include current active pattern in search in DEV mode will add also tplre files from pattern folder.
        pattern_path_list = [local_cond['full_path']]

        # This mode executes only when I working in tplre development paths:
        if env_mode == 'developer_tplpre':

            # Step 1 - Find pattern files in current pattern folder:
            pattern_path_list = self.list_folder(self.working_dir)

            # Add some extra pattens from test.py if 'read_tests' arguments was set and sorted in GlobalLogic:
            if extra_patterns:
                for p in extra_patterns:
                    if p not in pattern_path_list:
                        pattern_path_list.append(p)
            log.debug("Step 1.1. Find modules for: "+str(pattern_path_list))

        # Start initial read of pattern files I have already and compose first search list of modules.
        find_importing_modules, current_modules_name = self.read_pattern(pattern_path_list,
                                                                         find_importing_modules,
                                                                         current_modules_name)

        log.debug("Step 2. Modules to find: "+str(find_importing_modules))

        # After first read of modules - start recursive search and read for all modules until found each:
        self.recursive_imports(current_modules_name   = current_modules_name,
                               find_importing_modules = find_importing_modules,
                               extra_folders          = extra_folders,
                               env_mode               = env_mode)

    def recursive_imports(self, **importing_set_options):
        """
        This functions does recursive imports based on local arguments
        and previously extracted modules from active pattern.

        It use
            -   extra folders for recursive search,
            -   current_modules_name - as list of already found modules + paths to patterns with them,
            -   find_importing_modules - possible candidate to find in next iteration.

        Each time after first search func() will compare list of current with find modules and iterate +1 search until
        found all modules in each extra folder. 3 iterations is hardcoded and usually enough to found everything.
        When every module was found - loop breaks.


        New revision of this function:
            - no need to check folder existence - all check were done before call,
            - no need to list subdirs in extra_folders - now path will point to end path for each pattens lib.
            - kwargs used instead of args.

        Example:
            importing_set_options: {
                "extra_folders": [
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+",
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+",
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+",
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-LoadBalancer-2017-07-1-ADDM-11.1+",
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+",
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+",
                    "D:\\customer_path\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-System-2017-07-1-ADDM-11.1+"
                ],
                "find_importing_modules": [
                    "module SupportingFiles.CDM_Mapping",
                    "module DiscoveryFunctions",
                    "module SearchFunctions",
                    "module SupportingFiles.Cluster.Support"
                ],
                "current_modules_name": [
                    {
                        "path": "D:\\customer_path\\TKU\\
                        Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+\\BMCRemedyARSystem.tpl",
                        "module": "module BMC.RemedyARSystem"
                    }
                ]
            }


        :type importing_set_options: set list
        :return:
        """

        extra_folders               = importing_set_options['extra_folders']
        current_modules_name        = importing_set_options['current_modules_name']
        find_importing_modules      = importing_set_options['find_importing_modules']
        env_mode                    = importing_set_options['env_mode']

        exclude_dirs = ['imports'
                        'tests',
                        'tpl',
                        'dml',
                        'expected',
                        'actuals',
                        'HarnessFiles'
                        ]

        # Make pattern list to found in each:
        all_patterns_list = self.files_to_read(env_mode=env_mode,
                                               search_path=extra_folders,
                                               exclude_dirs=exclude_dirs)

        iteration_count = 0
        while iteration_count < 3:
            # Recursive search for imports and imports for found patterns for 3 times.
            # If something was not found on 3rd iteration - print warning message with these items.
            iteration_count = iteration_count + 1
            if find_importing_modules:
                log.debug("Round: "+str(iteration_count)+" - of recursive search.")
                log.debug("Step 2.2. Searching modules from step 2")

                # Step 4. - Find modules which left in list - in other folders including CORE:
                find_2, current_2 = self.search_in_path(file_candidates        = all_patterns_list,
                                                        find_importing_modules = find_importing_modules,
                                                        current_modules_name   = current_modules_name)
                find_importing_modules = find_2
                current_modules_name = current_2

                if find_importing_modules:
                    # Clear list from already found modules which was added twice
                    for found in current_modules_name:
                        if found['module'] in find_importing_modules:
                            find_importing_modules.remove(found['module'])
            else:
                log.debug("Round: "+str(iteration_count)+" - Found everything already, breaking the loop.")
                break

        if find_importing_modules:
            log.warning("Step 3. These modules cannot be found anywhere in 'tku_patterns' "
                        "please check manually: "+str(find_importing_modules))
        if current_modules_name:
            log.debug("Step 3.1 Found modules list: "+str(current_modules_name))

        # Executing imports. Nothing to return as well.
        self.import_tkn(current_modules_name, self.working_dir)

    def read_pattern(self, pattern_path_list, find_importing_modules, current_modules_name):
        """
        Read pattern and store content
        Parse pattern obj and find imports section
        Save each found pattern module to list.

         1. Read imports and pattern module names from current patterns in pattern dir:

                - save list of [current_modules_name] (list of found modules + path to file) - this list will be used
                    to copy files into 'imports'

                - save list of [find_importing_modules] (list of modules we need to find) - exclude modules
                    from list of [current_modules_name]

        current_pattern_dict = {'module': 'module BMC.RemedyARSystem',
                                'path': 'D:\\FakePattern_folder\\FAKEPatternFileLiesHere.(tplpre|tpl)'}

        :param pattern_path_list: list of patterns to read in.
        :param find_importing_modules: incoming list of modules I need to find
        :param current_modules_name: incoming list of modules already found
        :return: list
        """

        if pattern_path_list:
            log.debug('Step 1.2. Reading patterns from the list.')
            for pattern in pattern_path_list:
                with open(pattern, encoding="utf8") as f:
                    read_file = f.read(2024)  # About 60+ lines from the beginning of pattern

                pattern_import = self.pattern_import_all_r.findall(read_file)

                # Check imports for pattern we found to add it to next search:
                current_pattern_module = self.pattern_module_name_r.findall(read_file)

                # When any imports were found in pattern file - add each to list and later find them:
                if pattern_import:
                    for pattern_module in pattern_import:
                        imports_line = "module " + pattern_module
                        if imports_line not in find_importing_modules:
                            find_importing_modules.append(imports_line)

                # Module name of currently read pattern was added to list also, to compare with already imported:
                if current_pattern_module:
                    current_module = "module " + current_pattern_module[0]
                    current_pattern_dict = dict(module = current_module,
                                                path   = pattern)

                    if current_pattern_dict not in current_modules_name:
                        current_modules_name.append(current_pattern_dict)
                else:
                    log.critical("I cannot read pattern module for: "+str(pattern))

            return find_importing_modules, current_modules_name
        else:
            log.warning("Nothing to read for read_pattern module. No imports will be found.")
            return False, False

    @staticmethod
    def files_to_read(env_mode, search_path, exclude_dirs):
        """
        Composing path to each pattern file in working directories or workspace.
        Then I will search modules to import through this list.

        This function looks odd, but I need to be sure I can walk each 1st level folders for each in tkn tree
        And the same variant should be used for customer - so I can have one module for both scenarios.

        Check if we have more than 1200 tplre files, means that all paths and patterns probably OK:
        >>> full_path_args = {
        ... 'STORAGE_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\STORAGE',
        ... 'BLADE_ENCLOSURE_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\BLADE_ENCLOSURE',
        ... 'CLOUD_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CLOUD',
        ... 'pattern_folder': 'BMCRemedyARSystem',
        ... 'full_path': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem\\\\BMCRemedyARSystem.tplpre',
        ... 'MIDDLEWAREDETAILS_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\MIDDLEWAREDETAILS',
        ... 'buildscripts_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\buildscripts',
        ... 'file_ext': 'tplpre',
        ... 'tku_patterns_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns',
        ... 'DBDETAILS_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\DBDETAILS',
        ... 'tkn_sandbox_t': 'd:\\\\perforce\\\\addm\\\\tkn_sandbox',
        ... 'MANAGEMENT_CONTROLLERS_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\MANAGEMENT_CONTROLLERS',
        ... 'LOAD_BALANCER_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\LOAD_BALANCER',
        ... 'SYSTEM_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\SYSTEM',
        ... 'working_dir': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem',
        ... 'env_cond': 'developer_tplpre',
        ... 'pattern_test_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem\\\\tests\\\\test.py',
        ... 'file_name': 'BMCRemedyARSystem',
        ... 'tkn_main_t': 'd:\\\\perforce\\\\addm\\\\tkn_main',
        ... 'CORE_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE',
        ... 'workspace': 'd:\\\\perforce'}
        >>> env_mode = "developer_tplpre"
        >>> search_path =  [
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\BLADE_ENCLOSURE',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CLOUD',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\DBDETAILS',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\LOAD_BALANCER',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\MANAGEMENT_CONTROLLERS',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\MIDDLEWAREDETAILS',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\SYSTEM',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\STORAGE']
        >>> exclude_dirs = ['importstests', 'tpl', 'dml', 'expected', 'actuals', 'HarnessFiles']
        >>> file_candidates = TPLimports(full_path_args).files_to_read(env_mode, search_path, exclude_dirs)
        >>> if len(file_candidates) > 1200:
        ...     print("True")
        ... else:
        ...     print("False")
        True

        # Clients test:
        >>> full_path_args = {
        ... 'full_path': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Core-2017-07-1-ADDM-11.1+\\\\BMCRemedyARSystem.tpl',
        ...  'MIDDLEWAREDETAILS_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+',
        ...  'tkn_sandbox_t': '',
        ...  'DBDETAILS_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+',
        ...  'working_dir': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Core-2017-07-1-ADDM-11.1+',
        ...  'env_cond': 'customer_tku',
        ...  'STORAGE_t': '',
        ...  'BLADE_ENCLOSURE_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+',
        ...  'file_ext': 'tpl',
        ...  'tku_patterns_t': '',
        ...  'LOAD_BALANCER_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-LoadBalancer-2017-07-1-ADDM-11.1+',
        ...  'SYSTEM_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-System-2017-07-1-ADDM-11.1+',
        ...  'file_name': 'BMCRemedyARSystem',
        ...  'CLOUD_t': '',
        ...  'MANAGEMENT_CONTROLLERS_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+',
        ...  'buildscripts_t': '',
        ...  'CORE_t': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Core-2017-07-1-ADDM-11.1+',
        ...  'pattern_folder': 'TKU-Core-2017-07-1-ADDM-11.1+',
        ...  'workspace': 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU',
        ...  'tkn_main_t': ''}
        >>> env_mode = "customer_tku"
        >>> search_path =  [
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+',
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Core-2017-07-1-ADDM-11.1+',
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+',
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-LoadBalancer-2017-07-1-ADDM-11.1+',
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-ManagementControllers-2017-07-1-ADDM-11.1+',
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+',
        ... 'D:\\\\perforce\\\\addm\\\\tkn_sandbox\\\\o.danylchenko\\\\Jira_fix\\\\TKU\\\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\\\TKU-System-2017-07-1-ADDM-11.1+']
        >>> exclude_dirs = ['importstests', 'tpl', 'dml', 'expected', 'actuals', 'HarnessFiles']
        >>> file_candidates = TPLimports(full_path_args).files_to_read(env_mode, search_path, exclude_dirs)
        >>> if len(file_candidates) >= 1110:
        ...     print("True")
        ... else:
        ...     print("False")
        True

        :param exclude_dirs:
        :param search_path: list
        :type env_mode: str
        :return: list
        """
        # print(env_mode, search_path, exclude_dirs)

        file_candidates = []

        if env_mode == 'developer_tplpre':
            log.debug("Step 2.1. - Composing list of all patterns in tkn path.")
            # Sort only tplpre files
            file_ext = ".tplpre"
            for path in search_path:
                for root, dirs, files in os.walk(path, topdown=True):
                    # Exclude service folders:
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    # Make path to each folder:
                    for folder in dirs:
                        folder_to_find = os.path.join(root, folder)
                        # List content of each folder in path and save if there is any file end with tplpre.
                        files_in = os.listdir(folder_to_find)
                        for file_p in files_in:
                            if file_p.endswith(file_ext):
                                # Make full path to tplpre file or files in folder:
                                file_candidate = os.path.join(root, folder, file_p)
                                if file_candidate not in file_candidates:
                                    # List with all available pattern files is ready to search with:
                                    file_candidates.append(file_candidate)

                    # Stop on first level, no need to jump deeper.
                    break

            return file_candidates

        elif env_mode == 'customer_tku':
            log.debug("Step 2.1. - Making list of all available patterns from extra folders to further search.")
            # Sort only tpl files
            file_ext = ".tpl"
            # Walk in each pattern module dir and get files in it:
            for path in search_path:
                for root, _, files_w in os.walk(path):
                    if 'imports' not in root:
                        for file in files_w:
                            # When file is .tpl - add to list of files we can use for read later.
                            if file.endswith(file_ext):
                                file_candidate = os.path.join(root, file)
                                # List with all available pattern files is ready to search with:
                                file_candidates.append(file_candidate)

            return file_candidates

        else:
            log.warning("I can import only pattern files tplre or tpl.")

    def search_in_path(self, file_candidates, find_importing_modules, current_modules_name):
        # noinspection SpellCheckingInspection
        """
        Search import modules by parsing each pattern in selected folder to find it.s module name.
        Add found patterns to [current_modules_name]

        current_modules_name = [{'module': 'module BMC.RemedyARSystem',
                                 'path': 'D:\\\\FakePattern_folder\\FAKEPatternFileLiesHere.(tplpre|tpl)'},]
        find_importing_modules = ['module Something.Some', 'module Doooooodidoo']

        Check when working in recursive imports without extra patterns.
        >>> full_path_args = {
        ... 'STORAGE_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\STORAGE',
        ... 'BLADE_ENCLOSURE_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\BLADE_ENCLOSURE',
        ... 'CLOUD_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CLOUD',
        ... 'pattern_folder': 'BMCRemedyARSystem',
        ... 'full_path': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem\\\\BMCRemedyARSystem.tplpre',
        ... 'MIDDLEWAREDETAILS_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\MIDDLEWAREDETAILS',
        ... 'buildscripts_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\buildscripts',
        ... 'file_ext': 'tplpre',
        ... 'tku_patterns_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns',
        ... 'DBDETAILS_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\DBDETAILS',
        ... 'tkn_sandbox_t': 'd:\\\\perforce\\\\addm\\\\tkn_sandbox',
        ... 'MANAGEMENT_CONTROLLERS_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\MANAGEMENT_CONTROLLERS',
        ... 'LOAD_BALANCER_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\LOAD_BALANCER',
        ... 'SYSTEM_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\SYSTEM',
        ... 'working_dir': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem',
        ... 'env_cond': 'developer_tplpre',
        ... 'pattern_test_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem\\\\tests\\\\test.py',
        ... 'file_name': 'BMCRemedyARSystem',
        ... 'tkn_main_t': 'd:\\\\perforce\\\\addm\\\\tkn_main',
        ... 'CORE_t': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE',
        ... 'workspace': 'd:\\\\perforce'}
        >>> imp = TPLimports(full_path_args).search_in_path(
        ... file_candidates=[
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\SupportingFiles\\\\'
        ... 'CDM_Mapping.tplpre',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\SupportingFiles\\\\'
        ... 'Cluster_Support.tplpre',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\SupportingFiles\\\\'
        ... 'DiscoveryFunctions.tplpre',
        ... 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\SupportingFiles\\\\'
        ... 'SearchFunctions.tplpre' ],
        ... find_importing_modules=[
        ... 'module SupportingFiles.CDM_Mapping',
        ... 'module DiscoveryFunctions',
        ... 'module SearchFunctions',
        ... 'module SupportingFiles.Cluster.Support'],
        ... current_modules_name=[{
        ... 'path': 'd:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\BMCRemedyARSystem\\\\'
        ... 'BMCRemedyARSystem.tplpre',
        ... 'module': 'module BMC.RemedyARSystem'}])
        >>> for dict in imp[1]:
        ...     print(dict['module'])
        ...     print(dict['path'])
        ... # doctest: +NORMALIZE_WHITESPACE
        module BMC.RemedyARSystem
        d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem\\BMCRemedyARSystem.tplpre
        module SupportingFiles.CDM_Mapping
        d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\CDM_Mapping.tplpre
        module SupportingFiles.Cluster.Support
        d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\Cluster_Support.tplpre
        module DiscoveryFunctions
        d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\DiscoveryFunctions.tplpre
        module SearchFunctions
        d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\SearchFunctions.tplpre

        :param file_candidates: list
        :param current_modules_name: list of module:pattern dicts I found
        :param find_importing_modules: list input with modules which I need to find
        :return: list
        """

        # In list of all available pattern files in searched tree -
        # search all we need to import by reading header of each file.
        # Step 2.1.- search in patterns list.
        for file in file_candidates:
            with open(file, "r", encoding="utf8") as f:
                read_file = f.read(2024)  # About 60+ lines from the beginning of pattern

            for pattern_module in find_importing_modules:
                # Compile re based on item from [find_importing_modules] -> module SupportingFiles.CDM_Mapping
                module_r = re.compile(pattern_module)
                # Check opened file with re composed from each [find_importing_modules]
                check_modules = module_r.findall(read_file)

                # When module name were found in opened file add each to list and later find them:
                if check_modules:
                    # Make dict as  current_modules_name
                    current_pattern_dict = dict(module = pattern_module,
                                                path   = file)
                    if current_pattern_dict not in current_modules_name:

                        # Clear Readonly flag before copying:
                        # This also will be duplicated in import_tkn() for other places in tkn tree
                        os.chmod(file, stat.S_IWRITE)
                        # Now copy released file:
                        current_modules_name.append(current_pattern_dict)
                        # Remove module which was found from list, then return list with modules left .
                        find_importing_modules.remove(pattern_module)

                    # Check imports for pattern we found to add it to next search:
                    pattern_import = self.pattern_import_all_r.findall(read_file)
                    # When any imports were found in pattern file add each to list and later find them:
                    if pattern_import:
                        for pattern_module_rec in pattern_import:
                            imports_line = "module " + pattern_module_rec
                            if imports_line not in find_importing_modules:
                                find_importing_modules.append(imports_line)

        log.debug("Step 2.2. - List of modules found and list of modules to find for next iteration.")
        return find_importing_modules, current_modules_name

    def import_tkn(self, patterns_path, working_dir):
        """
            Copy patterns to "imports" folder

            Create folder 'imports'
            Copy imported patterns in folder imports
            Then - syntax check will be started

            :param working_dir: string pattern folder
            :param patterns_path:
                    [{'module': 'module BMC.RemedyARSystem',
                    'path': 'D:\\\\FakePattern_folder\\FAKEPatternFileLiesHere.(tplpre|tpl)'},]
            :return:
        """

        imports_folder = working_dir + os.sep + "imports"

        # log.debug("Step 4. Patterns to be copied into 'imports': "+str(patterns_path))
        self._del_old_imports(imports_folder)
        if not os.path.exists(imports_folder):
            os.mkdir(imports_folder)

            log.debug("Step 5. Creating folder 'imports'.")
            for pattern in patterns_path:

                pattern_path = pattern['path']

                os.chmod(pattern_path, stat.S_IWRITE)
                shutil.copy2(pattern_path, imports_folder)

                log.debug("Step 5.1 Copy to 'imports' pattern: " + str(pattern['path']))

    # Service functions:
    @staticmethod
    def list_folder(folder_path):
        """
        Get working_dir content to find all
        Only for DEV scenario - because we have cases with two patterns in one folder.

        ['D:\\FakePattern_folder\\FAKEPatternFileLiesHere.tplpre']
        :param folder_path: str
        :return: list
        """

        all_tplre = []
        tplpre_path = []

        folder_content = os.listdir(folder_path)
        if folder_content:
            for file in folder_content:

                # This is not the best solution for customer mode, because it will parse whole patterns,
                # leave tplpre check here:
                if file.endswith(".tplpre"):
                    all_tplre.append(file)
                    tplpre_path.append(folder_path + os.sep + file)
                    # break

            log.debug("Step 1. List of patterns in current active folder: "+str(tplpre_path))

            return tplpre_path
        else:
            log.warning("Current folder is empty or does not exist. Please check arguments and path to current file.")

    def _del_old_imports(self, path):
        """
        Trying to delete imports folder situated in active pattern folder.

        :param path: path to imports folder
        :return:
        """
        if os.path.exists(path):
            try:
                log.debug("Step 4. Wiping 'imports' folder before add new imports in it. "+str(path))
                shutil.rmtree(path, onerror=self._del_rw)
                # shutil.rmtree(path)
            except TypeError as e:
                log.warning("Step 4.1 This folder exist but program have no permission to remove it. "
                            "Please check path and permissions and 'AR' attribute in file.")
                log.error(e)
                raise
            except PermissionError as e:
                log.warning("Step 4.1 This folder exist but program have no permission to remove it. "
                            "Please check path and permissions and 'AR' attribute in file.")
                log.error(e)
                raise

    @staticmethod
    def _del_rw(name):
        print(name)
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
