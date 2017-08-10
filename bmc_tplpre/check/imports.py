"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""


# TODO Import modules from pattern and copy to working dir

import re
import os
import shutil
import stat
import subprocess


class TPLimports:

    """
    New logic of imports will be used:

        Step 1: List patterns in current folder of active pattern.
        Step 1.1 - Step 1.2: Read patterns from current folders and extract import modules and pattern modules.
                  Add import modules to list which will be used for finding in extra places.
                  Add pattern modules to list which will be used to compare if we found and know this module already.
        Step 1.3: Use list of found import modules from read pattern (Step 1.2) and start searching in extra places.

        Round: 1 - of recursive searching patterns.
            Step 2: Searching modules from each found pattern from Step 1.
                    Search in each sub folder of list of extra folders:
                    Add import modules to list which will be used for finding in extra places in next round.
                    Add pattern modules to list which will be used to compare if we found and know this module already.
            Step 2: in while execution:
                    Compare found module items with list of pattern modules which was already found and remove it match.

        Round: 2 - of recursive searching patterns.
            Repeat execution with vars from Round 1

        Round: 3 - of recursive searching patterns.
            Repeat execution with vars from Round 2
            Break the loop 'while < 3'

        Step 3: Show list of modules which wasn't found anywhere during 3 rounds in log warn.
        Step 3.1: Show list of found modules and path to patterns in log debug.

        Step 4: Wiping 'imports' folder before add new imports in it.
            Step 4.1 If folder cannot be wiped - show warning log.

        Step 5: Create 'imports' folder if isn't exist.
        Step 5.1: Copy pattern to imports folder and show debug log with path to copied pattern.


    """

    def __init__(self, logging, full_path_args):
        # TODO: Enhance imports logic to add places where to find different patterns.
        # TODO: Add list to import from test.py if args.
        # TODO: Check OS path and some settings to find TKN_CORE
        # First search in Supporting Files!

        """
        PATH ARGS: {'workspace': 'd:\\perforce',
                    'file_ext': 'tplpre',
                    'file_name': 'BMCRemedyARSystem',
                    'pattern_folder': 'BMCRemedyARSystem',
                    'tkn_main_t': 'd:\\perforce\\addm\\tkn_main\\',
                    'tkn_sandbox_t': 'd:\\perforce\\addm\\tkn_sandbox',
                    'buildscripts_t': 'd:\\perforce\\addm\\tkn_main\\\\buildscripts',
                    'tku_patterns_t': 'd:\\perforce\\addm\\tkn_main\\\\tku_patterns\\',
                    'CORE_t': 'd:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE',
                    'SupportingFiles_t': 'd:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles',
                    'MIDDLEWAREDETAILS_t': 'd:\\perforce\\addm\\tkn_main\\\\tku_patterns\\MIDDLEWAREDETAILS',
                    'DBDETAILS_t': 'd:\\perforce\\addm\\tkn_main\\\\tku_patterns\\DBDETAILS\\Database_Structure_Patterns',
                    'working_dir': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem',
                    'full_path': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\BMCRemedyARSystem\\BMCRemedyARSystem.tplpre'}

        :param logging: inherited log class
        :param full_path_args: args parsed and composed
        """

        self.logging = logging
        log = self.logging

        self.full_path_args = full_path_args

        if self.full_path_args:

            # log.debug("PATH ARGS: "+str(self.full_path_args))

            self.workspace   = self.full_path_args['workspace']
            self.full_path   = self.full_path_args['full_path']
            self.working_dir = self.full_path_args['working_dir']
            self.file_ext    = self.full_path_args['file_ext']

            self.tku_patterns_t    = self.full_path_args['tku_patterns_t']
            self.CORE_t    = self.full_path_args['CORE_t']
            self.SupportingFiles_t    = self.full_path_args['SupportingFiles_t']
            self.MIDDLEWAREDETAILS_t    = self.full_path_args['MIDDLEWAREDETAILS_t']
            self.DBDETAILS_t    = self.full_path_args['DBDETAILS_t']

            log.debug("Arguments from -full_path are obtained and program will make decisions.")
        else:
            log.warn("Arguments from -full_path are'n obtained and program cannot make decisions.")

        self.pattern_import_all_r = re.compile('from\s+(.+?)\s+import\s+\S+\s+\d+')
        self.pattern_module_name_r = re.compile('tpl\s+\$\$TPLVERSION\$\$\s+module\s+(\S+);')

    def import_modules(self):
        """
            Run to import:
        :return: will be returned as function obj in global_logic
        """

        extra_folders = [
                         'BLADE_ENCLOSURE',
                         'CLOUD',
                         'CORE',
                         'DBDETAILS',
                         'LOAD_BALANCER',
                         'MANAGEMENT_CONTROLLERS',
                         'MIDDLEWAREDETAILS',
                         'STORAGE',
                         'SYSTEM'
                        ]

        log = self.logging
        log.debug("Step 0. Starting import functions.")

        # Set options:
        pattern_path_list = []  # List of patterns found
        current_modules_name = []  # Modules from KNOWN and FOUND and CURRENT.
        find_importing_modules = []  # Modules which I should found.
        found_import_modules = []  # Modules which I should found.

        # Step 1 - Find pattern files in current pattern folder:
        pattern_path_list = self.list_folder(self.working_dir)
        log.debug("Step 1.1. Finding modules for: "+str(pattern_path_list))

        # Step 2 - Read patterns from current folder and get [find_importing_modules] AND [current_modules_name]
        find_importing_modules, current_modules_name = self.read_pattern(pattern_path_list,
                                                                         find_importing_modules,
                                                                         current_modules_name)
        log.debug("Step 1.3. Searching modules from current pattern: "+str(find_importing_modules))

        iteration_count = 0
        while iteration_count < 3:

            # Recursive search for imports and imports for found patterns for 3 times.
            # If something was not found on 3rd iteration - print warn message with theese items.
            iteration_count = iteration_count + 1
            if find_importing_modules:
                log.debug("Round: "+str(iteration_count)+" - of recursive searching patterns.")
                log.debug("Step 2. Searching modules from each found pattern from Step 1 : "+str(find_importing_modules))

                for item in extra_folders:

                    # List folders of each folder in extra folders:
                    extra_folder = self.tku_patterns_t + os.sep + item
                    if os.path.exists(extra_folder):
                        extra_folder_folders = os.listdir(extra_folder)
                        log.debug("Round: "+str(iteration_count)+" - Search patterns in sub folders in directory: "+str(extra_folder))

                        # In each sub folder from extra folders find:
                        for folder in extra_folder_folders:
                            directory = extra_folder + os.sep + folder

                            if os.path.isdir(directory):
                                # Step 4. - Find modules which left in list - in other folders including CORE:
                                find_importing_modules_2, current_modules_name_2 = self.search_in_path(search_path=directory,
                                                                                                       find_importing_modules=find_importing_modules,
                                                                                                       current_modules_name=current_modules_name)
                                find_importing_modules = find_importing_modules_2
                                current_modules_name = current_modules_name_2

                                if find_importing_modules:
                                    # Clear list from already found modules which was added twice
                                    for found in current_modules_name:
                                        if found['module'] in find_importing_modules:
                                            find_importing_modules.remove(found['module'])
                    else:
                        log.warn("Round: "+str(iteration_count)+" - Cannot proceed because path is not exist: "+str(extra_folder))
            else:
                log.debug("Round: "+str(iteration_count)+" - Found everything already, no reason to continue loop.")

        if find_importing_modules:
            log.warn("Step 3. These modules cannot be found anywhere in 'tku_patterns' please check manually: "+str(find_importing_modules))
        if current_modules_name:
            log.debug("Step 3.1 Found modules list: "+str(current_modules_name))

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
                                'path': 'D:\\..\\..\\..\\..\\..\\FakePattern_folder\\FAKEPatternFileLiesHere.tplpre'}



        :param pattern_path_list: list of patterns to read in.
        :param find_importing_modules: incoming list of modules I need to find
        :param current_modules_name: incoming list of modules already found
        :return: list
        """
        log = self.logging

        log.debug('Step 1.2. List of patterns to read: '+str(pattern_path_list))

        for pattern in pattern_path_list:

            open_file = open(pattern)
            read_file = open_file.read(2024)  # About 60+ lines from the beginning of pattern
            open_file.close()

            pattern_import = self.pattern_import_all_r.findall(read_file)
            current_pattern_module = self.pattern_module_name_r.findall(read_file)

            # When any imports were found in pattern file add each to list and later find them:
            if pattern_import:
                for pattern_module in pattern_import:
                    imports_line = "module " + pattern_module
                    if imports_line not in find_importing_modules:
                        find_importing_modules.append(imports_line)

            # Module name of currently read pattern is adding to list also to compare with already imported:
            if current_pattern_module:
                current_module = "module " + current_pattern_module[0]
                current_pattern_dict = {'module': current_module, 'path': pattern}
                if current_pattern_dict not in current_modules_name:
                    current_modules_name.append(current_pattern_dict)
            else:
                log.critical("I cannot read pattern module for: "+str(pattern))

        return find_importing_modules, current_modules_name

    def search_in_path(self, search_path, find_importing_modules, current_modules_name):
        """
        Search import modules by parsing each pattern in selected folder to find it.s module name.
        Add found patterns to [current_modules_name]

        current_modules_name = [{'module': 'module BMC.RemedyARSystem',
                                 'path': 'D:\\..\\..\\..\\..\\..\\FakePattern_folder\\FAKEPatternFileLiesHere.tplpre'},]
        find_importing_modules = ['module Something.Some', 'module Doooooodidoo']

        :param current_modules_name: list of module:pattern dicts I found
        :param find_importing_modules: list input with modules which I need to find
        :type search_path: path to folder where to search imports
        :return: list
        """

        folder_content = os.listdir(search_path)
        for file in folder_content:
            if file.endswith(".tplpre"):

                open_file = open(search_path + os.sep + file, "r")
                read_file = open_file.read(2024) # About 30+ lines from the beggining of pattern
                open_file.close()

                for pattern_module in find_importing_modules:
                    # Compile re based on item from [find_importing_modules] -> module SupportingFiles.CDM_Mapping
                    module_r = re.compile(pattern_module)
                    # Check opened file with re composed from each [find_importing_modules]
                    check_modules = module_r.findall(read_file)

                    # When module name were found in opened file add each to list and later find them:
                    if check_modules:
                        pattern_file_path = search_path + os.sep + file # Save path to current file

                        # Make dict as  current_modules_name
                        current_pattern_dict = {'module': pattern_module, 'path': pattern_file_path}
                        if current_pattern_dict not in current_modules_name:
                            # Clear Readonly flag before copying:
                            os.chmod(pattern_file_path, stat.S_IWRITE)
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
                    'path': 'D:\\..\\..\\..\\..\\..\\FakePattern_folder\\FAKEPatternFileLiesHere.tplpre'},]
            :return:
        """

        log = self.logging
        imports_folder = working_dir + os.sep + "imports"

        # log.debug("Step 4. Patterns to be copied into 'imports': "+str(patterns_path))
        self._del_old_imports(imports_folder)
        if not os.path.exists(imports_folder):
            os.mkdir(imports_folder)

            log.debug("Step 5. Creating folder 'imports' and add imported patterns.")
            for pattern in patterns_path:
                shutil.copy2(pattern['path'], imports_folder)

                log.debug("Step 5.1 Copy pattern to imports folder: " + str(pattern['path']))


        return

    # Service functions:
    def list_folder(self, folder_path):
        """
        Get working_dir content to find all tplpre

        ['D:\\..\\..\\..\\..\\..\\FakePattern_folder\\FAKEPatternFileLiesHere.tplpre']
        :param folder_path: str
        :return: list
        """
        log = self.logging

        all_tplre = []
        tplpre_path = []

        folder_content = os.listdir(folder_path)
        for file in folder_content:

            if file.endswith(".tplpre"):
                all_tplre.append(file)
                tplpre_path.append(folder_path + os.sep + file)
                # break

        log.debug("Step 1. List of patterns in current active folder: "+str(tplpre_path))

        return tplpre_path

    def _del_old_imports(self, path):
        """
        Trying to delete imports folder situated in active pattern folder.

        :param path: path to imports folder
        :return:
        """
        log = self.logging
        if os.path.exists(path):
            try:
                log.debug("Step 4. Wiping 'imports' folder before add new imports in it. "+str(path))
                shutil.rmtree(path, onerror=self._del_rw)
                # shutil.rmtree(path)
            except:
                log.warn("Step 4.1 This folder exist but programm have no permission to remove it. "
                         "Please check path and permissions and 'AR' attribute in file.")
                raise

    @staticmethod
    def _del_rw(name):
        print(name)
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)

    # OLD functions but still can be helpful:
    def OLD_new_search_in_path(self, search_path, modules_left_to_add):
        """
        Logic to search in CORE or something.
            List folders in CORE
            Check each item is this really folder
            List each folder and check file end with .tplpre
            Ignore folder SupportingFiles
            File open and search for module
            If found - add to list and remove from modules list which added


        :param modules_left_to_add:
        :param import_modules_list:
        :param search_path:
        :return:
        """
        log = self.logging
        import_modules_patterns = []

        log.debug("Step 4.2 Now I'll search modules which left in : "+str(search_path))
        log.debug("Step 4.2 Those modules should be imported from : "+str(modules_left_to_add))
        core_folders_list = os.listdir(search_path)
        for pattern_folder in core_folders_list:
            if not pattern_folder  == "SupportingFiles":
                pattern_folder_path = search_path+os.sep+pattern_folder
                if os.path.isdir(pattern_folder_path):
                    files = os.listdir(pattern_folder_path)
                    for file in files:
                        if file.endswith(".tplpre"):
                            pattern_file_path = pattern_folder_path+os.sep+file
                            open_file = open(pattern_file_path, "r")
                            read_file = open_file.read(512) # About 10+ lines from the beggining of pattern
                            open_file.close()

                            for pattern_module in modules_left_to_add:
                                module_r = re.compile(pattern_module)
                                check_modules = module_r.findall(read_file)

                                if check_modules:
                                    if pattern_file_path not in import_modules_patterns:
                                        # Clear Readonly flag before copying:
                                        os.chmod(pattern_file_path, stat.S_IWRITE)
                                        # Now copy released file:
                                        import_modules_patterns.append(pattern_file_path)
                                        # Remove module which was found from list, then return list with modules left .
                                        modules_left_to_add.remove(pattern_module)

        return import_modules_patterns, modules_left_to_add

    def OLD_import_modules_old(self):
        """
        Summarize all imports

        module_imports: ['module SupportingFiles.CDM_Mapping', 'module SupportingFiles.RDBMS_Functions',
                         'module DiscoveryFunctions', 'module SearchFunctions', 'module RDBMSFunctions',
                         'module J2EE.InferredModel', 'module IBMTivoliMonitoringCommonFunctions',
                         'module XenDesktopAppFunctions', 'module Apache.Hadoop', 'module Citrix.XenAppFuncs',
                         'module IBM.Cognos.Common_Code', 'module RedHat.JBossFuncs', 'module VMware_Functions',
                         'module Oracle.ApplicationServer', 'module SupportingFiles.Cluster.Support',
                         'module Microsoft.SQLServer_VersionTables', 'module Microsoft.SQL_Server_Modern_Versions']

        import_list: ['D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\CDM_Mapping.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\Cluster_Support.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\DiscoveryFunctions.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\IBMTivoliMonitoringCommonFunctions.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\J2EEInferredModel.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\RDBMSFunctions.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\RDBMS_Functions.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\SearchFunctions.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\\\tku_patterns\\CORE\\SupportingFiles\\Common_Functions.tplpre',
                      'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\FakePattern_folder\\FAKEPatternFileLiesHere.tplpre']

        :return: True if imports were successful.
        """

        log = self.logging

        # Step 1 - Find pattern files in current pattern folder:
        pattern_path_list = self.list_folder(self.working_dir)
        # print("Patterns I found in current folder: "+str(pattern_path_list))

        # Step 2 - Read each found pattern file to obtain import strings:
        if pattern_path_list:
            module_imports = self.read_pattern(pattern_path_list)

        # Step 3 - Compose list of imports:
        if module_imports:
            import_list = self.pattern_imports(import_modules=module_imports, folder_path=self.working_dir)

        # Step 4 - Add current active pattern to copy itself to imports folder:
        log.debug("Step 4. Copy current pattern(s) from pattern folder: "+str(pattern_path_list))
        for pattern in pattern_path_list:
            import_list.append(pattern)

        # if import_list:
        #     log.debug("Step 3. Importing patterns: "+str(import_list))
        # else:
        #     log.debug("Step 3. Import modules not found in pattern file")

        # Step 5. Copy imported patterns into imports folder
        self.import_tkn(import_list, self.working_dir)

        return True

    def OLD_pattern_imports(self, folder_path, import_modules):
        """
        Collect import modules, find them


        INPUT:
        import_modules = ['module SupportingFiles.CDM_Mapping',
                          'module DiscoveryFunctions',
                          'module SearchFunctions',
                          'module SupportingFiles.Cluster.Support',
                          'module ApacheFoundation.Tomcat',
                          'module J2EE.InferredModel',
                          'module RDBMSFunctions']

        folder_path = 'D:\Doc\PerForce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem'


        OUTPUT:
        [{'module_name': 'module SupportingFiles.CDM_Mapping', 'pattern_file': 'd:\\Doc\\PerForce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\CDM_Mapping.tplpre'},
         {'module_name': 'module SupportingFiles.Cluster.Support', 'pattern_file': 'd:\\Doc\\PerForce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\Cluster_Support.tplpre'},
         {'module_name': 'module DiscoveryFunctions', 'pattern_file': 'd:\\Doc\\PerForce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\DiscoveryFunctions.tplpre'},
         {'module_name': 'module J2EE.InferredModel', 'pattern_file': 'd:\\Doc\\PerForce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\J2EEInferredModel.tplpre'},
         {'module_name': 'module RDBMSFunctions', 'pattern_file': 'd:\\Doc\\PerForce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\RDBMSFunctions.tplpre'},
         {'module_name': 'module SearchFunctions', 'pattern_file': 'd:\\Doc\\PerForce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles\\SearchFunctions.tplpre'}]

        :type folder_path: str
        :param import_modules: list
        :return: list
        """

        log = self.logging

        extra_folders = [
                         'BLADE_ENCLOSURE',
                         'CLOUD',
                         'DBDETAILS',
                         'LOAD_BALANCER',
                         'MANAGEMENT_CONTROLLERS',
                         'MIDDLEWAREDETAILS',
                         'STORAGE',
                         'SYSTEM'
                        ]

        log.debug("Step 3. Compose imports lists of modules: "+str(import_modules))

        # Search in Supporting Files first
        import_modules_patterns, modules_left = self.old_search_in_path(search_path=self.SupportingFiles_t,
                                                                        import_modules_list=import_modules)
        if import_modules_patterns:
            log.debug("Step 4.2 I found those patterns in current file and will add them to "
                      "imports: "+str(import_modules_patterns))
            for module_pattern in import_modules_patterns:
                if module_pattern not in import_modules_patterns:
                    import_modules_patterns.append(module_pattern)

        # Then if something left, search in CORE:
        # Search in CORE and append found patterns to [import_modules_patterns] list
        if modules_left:
            # self.search_in_path(search_path=self.CORE_t, modules_left_to_add=modules_left)
            import_modules_patterns, modules_left = self.search_in_path(search_path=self.CORE_t,
                                                                        modules_left_to_add=modules_left)
            if import_modules_patterns:
                log.debug("Step 4.2 I found those patterns in CORE and will add them to "
                          "imports: "+str(import_modules_patterns))
                for module_pattern in import_modules_patterns:
                    if module_pattern not in import_modules_patterns:
                        import_modules_patterns.append(module_pattern)

            if modules_left:
                # TODO: Import modules from:
                # ['MIDDLEWAREDETAILS','BLADE_ENCLOSURE','DBDETAILS','LOAD_BALANCER','MANAGEMENT_CONTROLLERS',
                # 'STORAGE','SYSTEM', 'CLOUD']
                log.debug("Step 4.3 Those modules was not found in CORE and in SupportingFiles "
                          "so I will check other places in tkn tree: "+str(modules_left))
                for folder in extra_folders:
                    extra_folder = self.tku_patterns_t + os.sep + folder

                    import_extra_modules_patterns, modules_left = self.search_in_path(search_path=extra_folder,
                                                                                      modules_left_to_add=modules_left)
                    if import_extra_modules_patterns:
                        log.debug("Step 4.3 I found some extra modules: "+str(import_extra_modules_patterns))
                        for extra_module_pattern in import_extra_modules_patterns:
                            if extra_module_pattern not in import_modules_patterns:
                                import_modules_patterns.append(extra_module_pattern)

                    # if modules_left:
                    #     # Last run for CORE:
                    #     import_modules_patterns, modules_left = self.search_in_path(search_path=self.CORE_t,
                    #                                                                 modules_left_to_add=modules_left)
                    #     if import_modules_patterns:
                    #         log.debug("Step 4.2 I found those patterns in CORE and will add them to "
                    #                   "imports: "+str(import_modules_patterns))
                    #         for module_pattern in import_modules_patterns:
                    #             if module_pattern not in import_modules_patterns:
                    #                 import_modules_patterns.append(module_pattern)
                    #     if modules_left:
                    #         log.info("OOPS! Step 4.3 Some extra modules are still does not found. "
                    #                  "Please ask author to handle "
                    #                  "this and show paths to those modules: "+str(modules_left))

        # import_modules_patterns - is a list of patterns to copy:
        if import_modules_patterns:
            # Check copying patterns for imports:
            imports = self.read_pattern(import_modules_patterns)
            import_modules_patterns_add, modules_left = self.old_search_in_path(search_path=self.SupportingFiles_t,
                                                                                import_modules_list=imports)
            if modules_left:
                log.debug("Step 4.1. Second imports modules left: "+str(modules_left))

            # Append new found patterns from second search to copy list:
            for additional_imports in import_modules_patterns_add:
                # Check list should not contain duplicates
                if additional_imports not in import_modules_patterns:
                    import_modules_patterns.append(additional_imports)

        log.debug("Step 3. List of modules to import with path to each: "+str(import_modules_patterns))

        return import_modules_patterns