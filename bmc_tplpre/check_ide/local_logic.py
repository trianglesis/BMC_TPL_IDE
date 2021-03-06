"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import os
import re
import zipfile
import subprocess
# import datetime
import logging

log = logging.getLogger("check_ide.logger")


# noinspection PyPep8Naming
class LocalLogic:

    def __init__(self):
        """
        Gathering local options based on filesystem arguments and cmd results got on working machine.
        And some extra results from external addm machine.
        """

        # TPL versions check_ide:
        self.tpl_ver_check = re.compile("\d+\.\d+")  # TPl ver 10.2,11.0...

        """
        Below in dicts should be updated manually each new ADDM release (not TKU release!)

        '11.3': 'tpl115',
        '11.2': 'tpl114',
        '11.1': 'tpl113',
        '11.0': 'tpl112',
        '10.2': 'tpl110',
        '10.1': 'tpl19',
        '10.0': 'tpl18',
        '9.0': 'tpl17',
        '8.3': 'tpl16',
        """
        self.tpl_folder_k = {
                             '1.20': 'tpl120',
                             '1.19': 'tpl119',
                             '1.18': 'tpl118',
                             '1.17': 'tpl117',
                             '1.16': 'tpl116',
                             '1.15': 'tpl115',
                             '1.14': 'tpl114',
                             '1.13': 'tpl113',
                             '1.12': 'tpl112',
                             '1.10': 'tpl110',
                             '1.9': 'tpl19',
                             '1.8': 'tpl18',
                             '1.7': 'tpl17',
                             '1.6': 'tpl16'
                             }

        self.PRODUCT_VERSIONS = {
                                 '11.8': 'NoName_11_8',
                                 '11.7': 'NoName_11_7',
                                 '11.6': 'NoName_11_6',
                                 '11.5': 'NoName_11_5',
                                 '11.4': 'EasterEgg',
                                 '11.3': 'DoubleDecker',
                                 '11.2': 'CustardCream',
                                 '11.1': 'Bobblehat',
                                 '11.0': 'Aardvark',
                                 '10.2': 'Zythum',
                                 '10.1': 'Zed',
                                 '10.0': 'Yodel'
                                 }

        self.TPL_VERSIONS = {
                             'NoName_11_8':      '1.20',
                             'NoName_11_7':      '1.19',
                             'NoName_11_6':      '1.18',
                             'NoName_11_5':      '1.17',
                             'EasterEgg':        '1.16',
                             'DoubleDecker':     '1.15',
                             'Bobblehat':        '1.13',
                             'Aardvark':         '1.12',
                             'Zythum':           '1.10',
                             'Zed':              '1.9',
                             'Yodel':            '1.8'
                             }

        # Compose regex for all file types and places:
        # Firstly check_ide if this path is usual DEV
        self.dev_path_re = re.compile('(\S+)(\\\\addm\\\\tkn_main\\\\tku_patterns\\\\)')

        # These parts of regex will be used to compose different trees:
        workspace_rs      = '(?P<workspace>\S+)'
        addm_rs           = '(?P<addm>addm)'
        tkn_main_rs       = '(?P<tkn_main>tkn_main)'
        tku_patterns_rs   = '(?P<tku_patterns>tku_patterns)'
        pattern_lib_rs    = '(?P<pattern_lib>[^\\\\]+)'

        pattern_folder_rs = '(?P<pattern_folder>[^\\\\]+)'

        tpl_folder_rs     = '(?P<tpl_folder>tpl\d+)'
        file_name_rs      = '(?P<file_name>\S+)\.'
        file_ext_rs       = '(?P<file_ext>\S+)'

        win_esc = '\\\\'

        '''
        Composing different REGEX strings to get args for different types of files in path:
        
        - Path to usual tplpre 
            path_parse_re:
            
            Path: D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\PatternFolder\\Pattern_Name.tplpre
                
                Re: (?P<workspace>\S+)\\(?P<addm>addm)\\(?P<tkn_main>tkn_main)\\
                    (?P<tku_patterns>tku_patterns)\\(?P<pattern_lib>[^\\]+)\\(?P<pattern_folder>[^\\]+)\\
                    (?P<file_name>\S+)\.(?P<file_ext>\S+)
        
        - Path to tpl in tplpre (After Preproc) - this probably can differ due to 'imports' folder in it.

            tpl_path_parse_re:
            Path: D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\PatternFolder\\tpl114\\Pattern_Name.tpl
                
                Re: (?P<workspace>\S+)\\(?P<addm>addm)\\(?P<tkn_main>tkn_main)\\
                    (?P<tku_patterns>tku_patterns)\\(?P<pattern_lib>[^\\]+)\\(?P<pattern_folder>[^\\]+)\\
                    (?P<tpl_folder>tpl\d+)\\(?P<file_name>\S+)\.(?P<file_ext>\S+)

        
        '''
        self.path_parse_re = re.compile(workspace_rs      + win_esc +
                                        addm_rs           + win_esc +
                                        tkn_main_rs       + win_esc +
                                        tku_patterns_rs   + win_esc +
                                        pattern_lib_rs    + win_esc +
                                        pattern_folder_rs + win_esc +
                                        file_name_rs      + file_ext_rs)

        self.tpl_path_parse_re = re.compile(workspace_rs      + win_esc +
                                            addm_rs           + win_esc +
                                            tkn_main_rs       + win_esc +
                                            tku_patterns_rs   + win_esc +
                                            pattern_lib_rs    + win_esc +
                                            pattern_folder_rs + win_esc +
                                            tpl_folder_rs     + win_esc +
                                            file_name_rs      + file_ext_rs)

        self.tkn_core_parse_re = re.compile(workspace_rs      + win_esc +
                                            addm_rs           + win_esc +
                                            tkn_main_rs       + win_esc +
                                            tku_patterns_rs)

        self.groups_alone_tplpre_re = re.compile('(?P<pattern_path>\S+)\\\\'
                                                 '(?P<pattern_folder>\S+)\\\\'
                                                 '(?P<file_name>\w+)\.(?P<file_ext>tplpre)')

        # Check TKU package path:
        self.tku_path_re = re.compile('(\S+)\\\\Technology-Knowledge-Update-\d+-\d+-\d+-ADDM-\d+\.\d+\+')

        # Parse TKU package:
        '''
        Example:
            working_dir: 'D:\custom\TKU\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\TKU-Core-2017-07-1-ADDM-11.1+'
            tku_update_path: 'D:\custom\TKU\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+'
            workspace: 'D:\custom\TKU'
            tku_package: 'Technology-Knowledge-Update'
            tku_package_year: '2017'
            tku_package_month: '07'
            tku_package_day: '1'
            tku_package_ADDM_ver: '11.1'
            tku_package_name: 'Core'
            pattern_folder: 'TKU-Core-2017-07-1-ADDM-11.1+'
            file_name: 'BMCRemedyARSystem'
            file_ext: 'tpl'
        '''

        # This is to check_ide and extract args from customer path, after unzip TKU Update package:
        self.tku_package_re = re.compile('(?P<working_dir>'
                                         '(?P<tku_update_path>'
                                         '(?P<workspace>\S+)\\\\'
                                         '(?P<tku_package>Technology-Knowledge-Update)-'
                                         '(?P<tku_package_year>\d+)-'
                                         '(?P<tku_package_month>\d+)-'
                                         '(?P<tku_package_day>\d+)-ADDM-'
                                         '(?P<tku_package_ADDM_ver>\d+\.\d+)\+)\\\\'
                                         '(?P<pattern_folder>TKU-'
                                         '(?P<tku_package_name>\S+)-'
                                         '(?P=tku_package_year)-'
                                         '(?P=tku_package_month)-'
                                         '(?P=tku_package_day)-ADDM-'
                                         '(?P=tku_package_ADDM_ver)\+))\\\\'
                                         '(?P<file_name>\S+)\.'
                                         '(?P<file_ext>\S+)')
        # Getting names:
        self.tku_package_name_re = re.compile('TKU-'
                                              '(?P<tku_package_name>\S+)-'
                                              '(?P<tku_package_year>\d+)-'
                                              '(?P<tku_package_month>\d+)-'
                                              '(?P<tku_package_day>\d+)-ADDM-'
                                              '(?P<tku_package_ADDM_ver>\d+\.\d+)\+')

        # Different regex matrix for alone files:
        self.alone_pattern_re = re.compile('([^"]+)\.(tplpre|tpl)')
        self.alone_tplpre_re = re.compile(pattern_folder_rs + win_esc +
                                          file_name_rs      + '(?P<file_ext>tplpre)')
        self.alone_tpl_re = re.compile(pattern_folder_rs + win_esc +
                                       file_name_rs      + '(?P<file_ext>tpl)')

        # Parsing ADDM version:
        # BMC Discovery Version: 11.1.0.5 Release: 698363
        self.addm_version_full_re = re.compile("BMC\sDiscovery\sVersion:\s+(\d+(?:\.\d+)*)")
        self.addm_version_re = re.compile("^(\d+(?:\.\d+)?)")

        # HGFS ADDM folder shares check_ide
        self.hgfs_path_re = re.compile("(?P<tkn_path>\S+)/addm/tkn_main/tku_patterns/"
                                       "(?:CORE|DBDETAILS|MANAGEMENT_CONTROLLERS|MIDDLEWAREDETAILS)")
        self.alter_shares_re = re.compile(r"/usr/tideway/TKU")
        self.vm_tkn_path_re = re.compile("(?P<tkn_path>\S+)/addm/tkn_main/tku_patterns/")

    @staticmethod
    def addm_compose_paths(dev_vm_path, pattern_folder):
        """
        Local path will be used to compose same path in remote vm if HGFS shares confirmed.
        To further usage I also compose path to remote test.py
        :return:
        """
        # Paths from local to remote:
        workspace = dev_vm_path

        tkn_main_virt = workspace + "/addm/tkn_main"
        tku_patterns_virt      = tkn_main_virt + "/tku_patterns"
        CORE_virt              = tku_patterns_virt + '/CORE'

        # Not used now, but can be later used:
        # buildscripts_virt      = tkn_main_virt + "/buildscripts"
        # MIDDLEWAREDETAILS_virt = tku_patterns_virt + '/MIDDLEWAREDETAILS'
        # DBDETAILS_virt         = tku_patterns_virt + '/DBDETAILS' + '/Database_Structure_Patterns'
        # SupportingFiles_virt   = tku_patterns_virt + '/CORE'      + '/SupportingFiles'

        # Composing working dir as in def full_path_parse() but now for remote mirror:
        working_dir_virt = CORE_virt+"/"+pattern_folder
        pattern_test_virt = working_dir_virt+"/tests/test.py"
        log.debug("Mirrored working dir for ADDM VM is: "+str(working_dir_virt))

        return working_dir_virt, pattern_test_virt

    @staticmethod
    def make_zip(path, module_name, mode_single=None):
        """
        Zip pattern files in path.
        :param mode_single: Zip files in folder or only one file.
        :param module_name: Name of pattern or its folder to create zip with its name.
        :param path: Path where tpl files are ready to be zipped.
        :return: zip path to ready zip file.
        """

        if not mode_single:
            norm_path = os.path.normpath(path+os.sep)
            path = norm_path+os.sep
            log.debug("ZIP: Making zip of all .tpl in folder:"  + norm_path)
            zip_filename = module_name + '.zip'
            zip_path = path + zip_filename

            try:
                patterns_zip = zipfile.ZipFile(zip_path, 'w')
                log.debug("ZIP: zip_filename:" + zip_filename)

                for foldername, subfolders, filenames in os.walk(norm_path):
                    for filename in filenames:
                        if filename != zip_filename:

                            patterns_zip.write(os.path.join(norm_path, filename), arcname=filename)
                            log.debug("ZIP: Adding pattern:" + filename)

                patterns_zip.close()
                log.debug("ZIP: zip_path: " + zip_path)
                return zip_path

            except FileNotFoundError as e:
                log.error("Patterns cannot be zipped because file path does not exist: "+str(e))
                return False
        else:
            norm_path = os.path.normpath(path)
            tpl_path = norm_path + '.tpl'
            zip_path = norm_path + '.zip'
            log.debug("ZIP: Zipping single file: " + tpl_path)
            zip_filename = module_name + '.zip'

            try:
                with zipfile.ZipFile(zip_path, 'w') as zip_pattern:
                    zip_pattern.write(tpl_path, arcname=module_name+'.tpl')

                log.debug("ZIP: zip_filename:" + zip_filename)
                log.debug("ZIP: Adding pattern:" + tpl_path)
                log.debug("ZIP: zip_path: " + zip_path)

                return zip_path

            except FileNotFoundError as e:
                log.error("Patterns cannot be zipped because file path does not exist: "+str(e))
                return False

    def file_path_decisions(self, full_file_path):
        """
        Get all available info from file path:
        - if dev file and path
        - if customer tree or p4
        - use file extension to decide what to do with file or files

        After all operations - function will create dict with all possible useful options for further processing.

        :param full_file_path: str
        :return: dict
        """

        # These should be filled with paths from p4 cmd or path parse.
        workspace                = ''
        working_dir              = ''
        tkn_main_t               = ''
        tku_patterns_t           = ''
        buildscripts_t           = ''
        BLADE_ENCLOSURE_t        = ''
        CLOUD_t                  = ''
        CORE_t                   = ''
        DBDETAILS_t              = ''
        LOAD_BALANCER_t          = ''
        MANAGEMENT_CONTROLLERS_t = ''
        MIDDLEWAREDETAILS_t      = ''
        STORAGE_t                = ''
        SYSTEM_t                 = ''
        tkn_sandbox_t            = ''
        tkn_core                 = ''
        EXTRAS_t = ''
        NETWORK_t = ''

        if os.path.exists(full_file_path):
            # log.debug("-full_file_path is: " + full_file_path)

            # Checking for different paths logic
            dev_path_check = self.dev_path_re.match(full_file_path)
            tku_path_check = self.tku_path_re.match(full_file_path)

            # Should match 'd:\perforce\addm\tkn_main\tku_patterns'
            if dev_path_check:
                log.debug("This is dev path. Will parse it to get args.")
                # Check full arguments:
                path_parse = self.path_parse_re.match(full_file_path)
                if path_parse:
                    # log.debug("Parsing path for options.")

                    # This should be always extracted if above checks passed:
                    workspace      = path_parse.group('workspace')
                    pattern_lib    = path_parse.group('pattern_lib')
                    pattern_folder = path_parse.group('pattern_folder')
                    file_name      = path_parse.group('file_name')
                    file_ext       = path_parse.group('file_ext')

                    # When workspace extracted - compose usual paths to each dev folder used in TKU:
                    tkn_main_t     = workspace  + os.sep + 'addm' + os.sep + 'tkn_main'
                    buildscripts_t = tkn_main_t + os.sep + 'buildscripts'
                    tku_patterns_t = tkn_main_t + os.sep + 'tku_patterns'

                    # Path to all pattern libs:
                    BLADE_ENCLOSURE_t        = tku_patterns_t+os.sep+'BLADE_ENCLOSURE'
                    CLOUD_t                  = tku_patterns_t+os.sep+'CLOUD'
                    CORE_t                   = tku_patterns_t+os.sep+'CORE'
                    EXTRAS_t                 = tku_patterns_t+os.sep+'EXTRAS_t'
                    DBDETAILS_t              = tku_patterns_t+os.sep+'DBDETAILS'
                    LOAD_BALANCER_t          = tku_patterns_t+os.sep+'LOAD_BALANCER'
                    MANAGEMENT_CONTROLLERS_t = tku_patterns_t+os.sep+'MANAGEMENT_CONTROLLERS'
                    MIDDLEWAREDETAILS_t      = tku_patterns_t+os.sep+'MIDDLEWAREDETAILS'
                    NETWORK_t                = tku_patterns_t+os.sep+'NETWORK'
                    STORAGE_t                = tku_patterns_t+os.sep+'STORAGE'
                    SYSTEM_t                 = tku_patterns_t+os.sep+'SYSTEM'

                    # Sandbox for extra functionality:
                    tkn_sandbox_t            = workspace+os.sep+'addm'+os.sep+'tkn_sandbox'

                    # Now check_ide file extensions for different options include:
                    if re.match('tplpre', file_ext):
                        # pattern working dir, where pattern file is really lies:
                        working_dir = tku_patterns_t+os.sep+pattern_lib+os.sep+pattern_folder
                        # Making prognoses place to test.py - but check_ide if exist in global logic mod
                        pattern_test_t = working_dir+os.sep+'tests'+os.sep+'test.py'

                        # Set of arguments, conditional options and paths to pattern libs:
                        args_dict = dict(
                                         env_cond                 = 'developer_tplpre',
                                         workspace                = workspace,
                                         pattern_folder           = pattern_folder,
                                         file_name                = file_name,
                                         file_ext                 = file_ext,
                                         working_dir              = working_dir,
                                         full_path                = full_file_path,
                                         tkn_main_t               = tkn_main_t,
                                         tku_patterns_t           = tku_patterns_t,
                                         buildscripts_t           = buildscripts_t,
                                         BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                         CLOUD_t                  = CLOUD_t,
                                         CORE_t                   = CORE_t,
                                         EXTRAS_t                 = EXTRAS_t,
                                         DBDETAILS_t              = DBDETAILS_t,
                                         LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                         MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                         MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                         NETWORK_t      = NETWORK_t,
                                         STORAGE_t                = STORAGE_t,
                                         SYSTEM_t                 = SYSTEM_t,
                                         tkn_sandbox_t            = tkn_sandbox_t,
                                         pattern_test_t           = pattern_test_t
                                         )
                        # log.info("Arguments from file path: " + str(args_dict))
                        log.debug("TPLPRE: File extension mach .tplpre and dev_path_check is found, "
                                  "options will be set based on it's path.")
                        return args_dict

                    # Check if this is a tpl file from: PatternFolder\tpl110\PatternName.tpl
                    elif re.match('tpl', file_ext):
                        log.info("File extension matched tpl pattern.")

                        path_parse     = self.tpl_path_parse_re.match(full_file_path)
                        pattern_folder = path_parse.group('pattern_folder')
                        file_name      = path_parse.group('file_name')
                        file_ext       = path_parse.group('file_ext')
                        tpl_folder     = path_parse.group('tpl_folder')

                        # pattern working dir, where pattern file is really lies:
                        working_dir = tku_patterns_t+os.sep+pattern_lib+os.sep+pattern_folder+os.sep+tpl_folder
                        # Making prognosable place to test.py - but check_ide if exist in global logic mod
                        pattern_test_t = working_dir+os.sep+'tests'+os.sep+'test.py'

                        args_dict = dict(
                                         env_cond                 = 'developer_tpl',
                                         workspace                = workspace,
                                         pattern_folder           = pattern_folder,
                                         file_name                = file_name,
                                         file_ext                 = file_ext,
                                         working_dir              = working_dir,
                                         full_path                = full_file_path,
                                         tkn_main_t               = tkn_main_t,
                                         tku_patterns_t           = tku_patterns_t,
                                         buildscripts_t           = buildscripts_t,
                                         BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                         CLOUD_t                  = CLOUD_t,
                                         CORE_t                   = CORE_t,
                                         EXTRAS_t                 = EXTRAS_t,
                                         DBDETAILS_t              = DBDETAILS_t,
                                         LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                         MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                         MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                         NETWORK_t                = NETWORK_t,
                                         STORAGE_t                = STORAGE_t,
                                         SYSTEM_t                 = SYSTEM_t,
                                         tkn_sandbox_t            = tkn_sandbox_t,
                                         pattern_test_t           = pattern_test_t
                                        )
                        return args_dict

                    # Check if this is a dml file from: ..\tests\dml\DML_DATA.dml
                    elif re.match('dml', file_ext):
                        log.debug("File extension matched dml pattern. DEV in progress...")
                        # TODO: Add pattern folder based on regex path to dml
                        log.debug("This is DML file.")
                        args_dict = dict(
                                         env_cond    = 'developer_dml',
                                         workspace                = workspace,
                                         pattern_folder           = pattern_folder,
                                         file_name                = file_name,
                                         file_ext                 = file_ext,
                                         working_dir              = '',
                                         full_path                = full_file_path,
                                         tkn_main_t               = tkn_main_t,
                                         tku_patterns_t           = tku_patterns_t,
                                         buildscripts_t           = buildscripts_t,
                                         BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                         CLOUD_t                  = CLOUD_t,
                                         CORE_t                   = CORE_t,
                                         EXTRAS_t                 = EXTRAS_t,
                                         DBDETAILS_t              = DBDETAILS_t,
                                         LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                         MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                         MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                         NETWORK_t                = NETWORK_t,
                                         STORAGE_t                = STORAGE_t,
                                         tkn_sandbox_t            = tkn_sandbox_t
                                        )
                        log.debug("Arguments from file path: " + str(args_dict))
                        log.debug("DML: File extension mach .dml and dev_path_check is found, "
                                  "options will be set based on it's path.")
                        # return args_dict
                        raise Exception("DML Files is not supported yet.")

                    # Check if this is a model file from: \tests\actuals\SI_MODEL.model
                    elif re.match('model', file_ext):
                        log.debug("File extension matched model pattern. DEV in progress...")
                        # TODO: Fix 'file_name': 'tests\\expected\\test10_Unix_ARSystem90'
                        # TODO: Add pattern folder based on regex path to model
                        log.debug("This is model file.")
                        args_dict = dict(
                                         env_cond    = 'developer_model',
                                         workspace                = workspace,
                                         pattern_folder           = pattern_folder,
                                         file_name                = file_name,
                                         file_ext                 = file_ext,
                                         working_dir              = '',
                                         full_path                = full_file_path,
                                         tkn_main_t               = tkn_main_t,
                                         tku_patterns_t           = tku_patterns_t,
                                         buildscripts_t           = buildscripts_t,
                                         BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                         CLOUD_t                  = CLOUD_t,
                                         CORE_t                   = CORE_t,
                                         EXTRAS_t                 = EXTRAS_t,
                                         DBDETAILS_t              = DBDETAILS_t,
                                         LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                         MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                         MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                         NETWORK_t                = NETWORK_t,
                                         STORAGE_t                = STORAGE_t,
                                         tkn_sandbox_t            = tkn_sandbox_t
                                        )
                        log.debug("Arguments from file path: " + str(args_dict))
                        log.debug("MODEL: File extension mach .model and dev_path_check is found, "
                                  "options will be set based on it's path.")
                        # return args_dict
                        raise Exception("MODEL Files is not supported yet.")

                    # Check if this is a py file from: ..\tests\test.py
                    elif re.match('py', file_ext):
                        log.debug("File extension matched py pattern. DEV in progress...")
                        # TODO: Add pattern folder based on regex path to model
                        log.debug("This is py file. Will check_ide if this is a 'test.py'")
                        args_dict = dict(
                                         env_cond    = 'developer_py',
                                         workspace                = workspace,
                                         pattern_folder           = pattern_folder,
                                         file_name                = file_name,
                                         file_ext                 = file_ext,
                                         working_dir              = '',
                                         full_path                = full_file_path,
                                         tkn_main_t               = tkn_main_t,
                                         tku_patterns_t           = tku_patterns_t,
                                         buildscripts_t           = buildscripts_t,
                                         BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                         CLOUD_t                  = CLOUD_t,
                                         CORE_t                   = CORE_t,
                                         EXTRAS_t                 = EXTRAS_t,
                                         DBDETAILS_t              = DBDETAILS_t,
                                         LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                         MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                         MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                         NETWORK_t                = NETWORK_t,
                                         STORAGE_t                = STORAGE_t,
                                         tkn_sandbox_t            = tkn_sandbox_t
                                        )
                        log.debug("Arguments from file path: " + str(args_dict))
                        log.debug("PY: File extension mach .py and dev_path_check is found, "
                                  "options will be set based on it's path.")
                        # return args_dict
                        raise Exception("PY Files is not supported yet.")

                    # If this file has an extension I do not support:
                    else:
                        raise Exception("FILE: Did not match any file extension "
                                        "I can use: 'tpl', 'tplpre', 'dml', 'model', 'test.py'")

                else:
                    raise Exception("Did not match TKU DEV pattern path tree! Will use another way to parse."
                                    "I expect path to file: d:\\P4\\addm\\tkn_main\\tku_patterns\\..\\..\\FileName.Ext")

            elif tku_path_check:
                log.info("Found Technology-Knowledge-Update path.")

                '''
                Example: 
                This dict will contain each module I found in folder TKU - 
                where Technology-Knowledge-Update-YY-MM-D-ADDM-VV.V+.zip extracted:
                    {
                      "bladeenclosure": {
                        "tku_package_name": "bladeenclosure",
                        "tku_package_path": "D:\\customer_path\\TKU\\
                        Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-BladeEnclosure-2017-07-1-ADDM-11.1+"
                      },
                      "core": {
                        "tku_package_name": "core",
                        "tku_package_path": "D:\\customer_path\\TKU\\
                        Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\TKU-Core-2017-07-1-ADDM-11.1+"
                      }
                '''

                # Check full arguments:
                tku_pack_parse = self.tku_package_re.match(full_file_path)
                if tku_pack_parse:
                    # log.debug("Parsing path for options.")

                    # Paths to TKU Update package tree:
                    working_dir          = tku_pack_parse.group('working_dir')
                    tku_update_path      = tku_pack_parse.group('tku_update_path')
                    workspace            = tku_pack_parse.group('workspace')
                    tku_package          = tku_pack_parse.group('tku_package')
                    tku_package_year     = tku_pack_parse.group('tku_package_year')
                    tku_package_month    = tku_pack_parse.group('tku_package_month')
                    tku_package_day      = tku_pack_parse.group('tku_package_day')
                    tku_package_ADDM_ver = tku_pack_parse.group('tku_package_ADDM_ver')
                    # tku_package_name     = tku_pack_parse.group('tku_package_name')

                    # As in dev scenario - this args pass to pattern folder:
                    pattern_folder       = tku_pack_parse.group('pattern_folder')
                    file_name            = tku_pack_parse.group('file_name')
                    file_ext             = tku_pack_parse.group('file_ext')

                    log.debug("I found following TKU Package details:"
                              " tku_update_path: "                      + str(tku_update_path)      +
                              " tku_package: "                          + str(tku_package)          +
                              " tku_package_year: "                     + str(tku_package_year)     +
                              " tku_package_month: "                    + str(tku_package_month)    +
                              " tku_package_day: "                      + str(tku_package_day)      +
                              " tku_package_ADDM_ver: "                 + str(tku_package_ADDM_ver) +
                              " Package situated in path: workspace: "  + str(workspace)
                              )

                    tku_dict = dict(tku_update           = tku_package,
                                    tku_update_path      = tku_update_path,
                                    tku_package_ADDM_ver = tku_package_ADDM_ver)

                    # Listing all other available packages:
                    tku_pack_tree = os.listdir(tku_update_path)
                    for item in tku_pack_tree:
                        item_match_tku = self.tku_package_name_re.match(item)
                        # Making path:
                        folder = tku_update_path+os.sep+item

                        if os.path.isdir(folder) and item_match_tku:
                            # For each matched package - make group with its details:
                            # Now adding each found package dir and its name to dict.
                            # In future we may want to check_ide each date and version before add, or not. Will see.
                            # List of packages dicts. Further will nested in tku_dict
                            tku_package_name     = item_match_tku.group('tku_package_name')
                            tku_package_year     = item_match_tku.group('tku_package_year')
                            tku_package_month    = item_match_tku.group('tku_package_month')
                            tku_package_day      = item_match_tku.group('tku_package_day')
                            tku_package_ADDM_ver = item_match_tku.group('tku_package_ADDM_ver')

                            log.debug("I found in current workspace other TKU Package with following details:"
                                      " tku_package_name: "     + str(tku_package_name)     +
                                      " tku_package_year: "     + str(tku_package_year)     +
                                      " tku_package_month: "    + str(tku_package_month)    +
                                      " tku_package_day: "      + str(tku_package_day)      +
                                      " tku_package_ADDM_ver: " + str(tku_package_ADDM_ver) +
                                      " Package path: "         + str(folder)
                                      )

                            '''
                            This should be in right format for further assignment to args dict:
                                {
                                  "bladeenclosure": {
                                    "tku_package_name": "bladeenclosure",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-BladeEnclosure-2017-07-1-ADDM-11.1+"
                                  },
                                  "core": {
                                    "tku_package_name": "core",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Core-2017-07-1-ADDM-11.1+"
                                  },
                                  "extended-db-discovery": {
                                    "tku_package_name": "extended-db-discovery",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Extended-DB-Discovery-2017-07-1-ADDM-11.1+"
                                  },
                                  "extended-middleware-discovery": {
                                    "tku_package_name": "extended-middleware-discovery",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-Extended-Middleware-Discovery-2017-07-1-ADDM-11.1+"
                                  },
                                  "loadbalancer": {
                                    "tku_package_name": "loadbalancer",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-LoadBalancer-2017-07-1-ADDM-11.1+"
                                  },
                                  "managementcontrollers": {
                                    "tku_package_name": "managementcontrollers",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-ManagementControllers-2017-07-1-ADDM-11.1+"
                                  },
                                  "system": {
                                    "tku_package_name": "system",
                                    "tku_package_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+\\
                                                            TKU-System-2017-07-1-ADDM-11.1+"
                                  },
                                  "tku_package_ADDM_ver": "11.1",
                                  "tku_update": "Technology-Knowledge-Update",
                                  "tku_update_path": "D:\\TKU\\Technology-Knowledge-Update-2017-07-1-ADDM-11.1+"
                                }
                                                                '''

                            # Each key should be the pattern lib name so further I can nest in args dict:
                            tku_package_name = tku_package_name.lower()
                            tku_solo_package_dict = {tku_package_name: {'tku_package_name': tku_package_name,
                                                                        'tku_package_path': folder}}

                            # noinspection PyTypeChecker
                            tku_dict.update(tku_solo_package_dict)

                    # Compose arguments based on previous extractions:
                    # noinspection PyTypeChecker
                    args_dict = dict(
                             env_cond    = 'customer_tku',
                             workspace                = workspace,
                             pattern_folder           = pattern_folder,
                             file_name                = file_name,
                             file_ext                 = file_ext,
                             working_dir              = working_dir,
                             full_path                = full_file_path,
                             tkn_main_t               = '',
                             tku_patterns_t           = '',
                             buildscripts_t           = '',
                             BLADE_ENCLOSURE_t        = tku_dict['bladeenclosure']['tku_package_path'],
                             CLOUD_t                  = '',
                             CORE_t                   = tku_dict['core']['tku_package_path'],
                             DBDETAILS_t              = tku_dict['extended-db-discovery']['tku_package_path'],
                             LOAD_BALANCER_t          = tku_dict['loadbalancer']['tku_package_path'],
                             MANAGEMENT_CONTROLLERS_t = tku_dict['managementcontrollers']['tku_package_path'],
                             MIDDLEWAREDETAILS_t      = tku_dict['extended-middleware-discovery']['tku_package_path'],
                             STORAGE_t                = '',
                             SYSTEM_t                 = tku_dict['system']['tku_package_path'],
                             tkn_sandbox_t            = ''
                                     )

                    # args_ord = json.dumps(args_dict, indent=4, ensure_ascii=False, default=pformat)
                    # print(args_ord)
                    return args_dict

            # When path to file has no tku_tree in. This is probably standalone file from anywhere.
            else:
                log.debug('FILE: There is no dev path in -full_path - '
                          'I expect "..\\addm\\tkn_main\\tku_patterns\\.." '
                          'Trying to locate place for alone pattern file.')

                # To be sure I have here - is a pattern file with tpl or tplre ext.
                # Also checking full path to file. No spaces or extra symbols allowed.
                alone_pattern_check = self.alone_pattern_re.match(full_file_path)
                if alone_pattern_check:
                    alone_tplpre_check = self.alone_tplpre_re.match(full_file_path)
                    # Sort tplpre:
                    if alone_tplpre_check:

                        # print(self.groups_alone_tplpre_re)
                        parse_alone_tplpre = self.groups_alone_tplpre_re.match(full_file_path)

                        # This is not actual 'workspace' this is just regex:
                        pattern_path   = parse_alone_tplpre.group('pattern_path')
                        pattern_folder = parse_alone_tplpre.group('pattern_folder')
                        file_name      = parse_alone_tplpre.group('file_name')
                        file_ext       = parse_alone_tplpre.group('file_ext')

                        workspace = self.workspace_find_p4_env()

                        # When workspace extracted - compose usual paths to each dev folder used in TKU:
                        tkn_main_t     = workspace  + os.sep + 'addm' + os.sep + 'tkn_main'
                        buildscripts_t = tkn_main_t + os.sep + 'buildscripts'
                        tku_patterns_t = tkn_main_t + os.sep + 'tku_patterns'

                        # Path to all pattern libs:
                        BLADE_ENCLOSURE_t        = tku_patterns_t+os.sep+'BLADE_ENCLOSURE'
                        CLOUD_t                  = tku_patterns_t+os.sep+'CLOUD'
                        CORE_t                   = tku_patterns_t+os.sep+'CORE'
                        DBDETAILS_t              = tku_patterns_t+os.sep+'DBDETAILS'
                        EXTRAS_t                 = tku_patterns_t+os.sep+'EXTRAS'
                        LOAD_BALANCER_t          = tku_patterns_t+os.sep+'LOAD_BALANCER'
                        MANAGEMENT_CONTROLLERS_t = tku_patterns_t+os.sep+'MANAGEMENT_CONTROLLERS'
                        MIDDLEWAREDETAILS_t      = tku_patterns_t+os.sep+'MIDDLEWAREDETAILS'
                        NETWORK_t                = tku_patterns_t+os.sep+'NETWORK'
                        STORAGE_t                = tku_patterns_t+os.sep+'STORAGE'
                        SYSTEM_t                 = tku_patterns_t+os.sep+'SYSTEM'
                        # Sandbox for extra functionality:
                        tkn_sandbox_t            = workspace+os.sep+'addm'+os.sep+'tkn_sandbox'

                        working_dir = pattern_path+os.sep+pattern_folder

                        log.debug("TPLPRE: This is alone tplpre file - will use path 'as is' "
                                  "To run TPLPreproc or Syntax check_ide - p4_path should be configured.")
                        # Set of arguments, conditional options and paths to pattern libs:
                        args_dict = dict(
                                         env_cond    = 'developer_tplpre',
                                         workspace                = workspace,
                                         pattern_folder           = pattern_folder,
                                         file_name                = file_name,
                                         file_ext                 = file_ext,
                                         working_dir              = working_dir,
                                         full_path                = full_file_path,
                                         tkn_main_t               = tkn_main_t,
                                         tku_patterns_t           = tku_patterns_t,
                                         buildscripts_t           = buildscripts_t,
                                         BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                         CLOUD_t                  = CLOUD_t,
                                         EXTRAS_t                 = EXTRAS_t,
                                         CORE_t                   = CORE_t,
                                         DBDETAILS_t              = DBDETAILS_t,
                                         LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                         MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                         MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                         NETWORK_t                = NETWORK_t,
                                         STORAGE_t                = STORAGE_t,
                                         SYSTEM_t                 = SYSTEM_t,
                                         tkn_sandbox_t            = tkn_sandbox_t
                                         )
                        return args_dict
                    # If not *.tlpre
                    else:
                        # See no reason to act with standalone tpl file OUT of usual dev environment or not?
                        # Or just upload it to ADDM?
                        # No imports or syntax check_ide will be run
                        #   - due unsupported set of options for single tpl in elsewhere in fs.
                        alone_tpl_check = self.alone_tpl_re.match(full_file_path)
                        # But then check_ide I have a proper *.tpl
                        if alone_tpl_check:
                            pattern_folder = alone_tpl_check.group('pattern_folder')
                            file_name      = alone_tpl_check.group('file_name')
                            file_ext       = alone_tpl_check.group('file_ext')
                            log.debug("Currently ignored option."
                                      "TPL: This is alone tpl file - will use path 'as is'."
                                      "Upload to ADDM and scan could be started if arguments was set.")
                            # Set of arguments, conditional options and paths to pattern libs:
                            args_dict = dict(
                                             env_cond    = 'developer_tplpre',
                                             workspace                = workspace,
                                             pattern_folder           = pattern_folder,
                                             file_name                = file_name,
                                             file_ext                 = file_ext,
                                             working_dir              = working_dir,
                                             full_path                = full_file_path,
                                             tkn_main_t               = tkn_main_t,
                                             tku_patterns_t           = tku_patterns_t,
                                             buildscripts_t           = buildscripts_t,
                                             BLADE_ENCLOSURE_t        = BLADE_ENCLOSURE_t,
                                             CLOUD_t                  = CLOUD_t,
                                             EXTRAS_t                 = EXTRAS_t,
                                             CORE_t                   = CORE_t,
                                             DBDETAILS_t              = DBDETAILS_t,
                                             LOAD_BALANCER_t          = LOAD_BALANCER_t,
                                             MANAGEMENT_CONTROLLERS_t = MANAGEMENT_CONTROLLERS_t,
                                             MIDDLEWAREDETAILS_t      = MIDDLEWAREDETAILS_t,
                                             NETWORK_t                = NETWORK_t,
                                             STORAGE_t                = STORAGE_t,
                                             SYSTEM_t                 = SYSTEM_t,
                                             tkn_sandbox_t            = tkn_sandbox_t
                                             )
                            return args_dict
                        else:
                            log.warning("This path did not match any suitable pattern and probably not a tpl file"
                                        " Or path has superfluous symbols or spaces")

                else:
                    raise FileNotFoundError("FILE: Cannot match file path for alone pattern. "
                                            "I expect: d:\\Something\\SomePattern.(tpl|tplpre)")

        else:
            # log.critical("No '-full_path' argument was set. Or this path is not exist!")
            raise FileNotFoundError("No '-full_path' argument was set. Or this path is not exist!")

    def workspace_find_p4_env(self):
        """
        When I found file tplpre - out of usual dev path - I can try to obtain workspace calling p4 cmd.
        Optionally I also can look for windows PATH for %TKN_CORE%

            Run p4 to obtain path: p4 -F %clientRoot% -ztag info
            C:\>p4 -F %clientRoot% -ztag info
            D:\perforce

            # Setting TKN_CORE from system variable or parse working directory for it


        :return: str
        """
        workspace_re = re.compile("(\S+)")
        log.info("Workspace was not found, trying p4 or PATH.")

        # noinspection PyBroadException
        try:
            run_p4 = subprocess.Popen('p4 -F %clientRoot% -ztag info',
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            stdout, stderr = run_p4.communicate()
            run_p4.wait()  # wait until command finished

            result = stdout.decode('UTF-8').rstrip('\r|\n')
            err_result = stderr.decode('UTF-8').rstrip('\r|\n')

            if result:
                # workspace_out = run_p4.stdout.read().decode()
                workspace = workspace_re.match(result).group(1)
                log.debug("Workspace was obtained from command run 'p4 -F %clientRoot% -ztag info'")
                return workspace

            if not result:
                # d:\perforce\addm\tkn_main\tku_patterns\
                tkn_core = os.environ.get("TKN_CORE")
                path_parse = self.tkn_core_parse_re.match(tkn_core)
                if path_parse:
                    workspace      = path_parse.group('workspace')
                    if workspace:
                        log.debug("Workspace was obtained from windows PATH env - '%TKN_CORE%'")
                        return workspace
            if err_result:
                log.error("P4 workspace cmd fail: "+str(err_result))
        except:
            log.error("CMD for p4 workspace won't run.")

    # noinspection PyBroadException
    def check_addm_tpl_ver(self, ssh):
        """
        Run command "tw_pattern_management -v"
        Parse version and compare with version dict.
        :param ssh:
        :return:
        """
        tpl_vers = ''
        addm_prod = ''
        addm_ver = ''
        tpl_folder = ''

        try:
            _, stdout, stderr = ssh.exec_command("tw_pattern_management -v")
            if stdout:

                output = stdout.readlines()
                addm_version_full = self.addm_version_full_re.match(output[0])
                addm_version = self.addm_version_re.match(addm_version_full.group(1))
                addm_ver = str(addm_version.group(1))

                if addm_ver in self.PRODUCT_VERSIONS:
                    addm_prod = self.PRODUCT_VERSIONS[addm_ver]
                    tpl_vers = self.TPL_VERSIONS[addm_prod]
                    if tpl_vers in self.tpl_folder_k:
                        tpl_folder = self.tpl_folder_k[tpl_vers]

            if stderr:
                err = stderr.readlines()
                if err:
                    log.warning("ADDM versioning command fails with error: " + str(err))
        except:
            log.error("Cannot run 'tw_pattern_management -v' command on ADDM!")

        return tpl_vers, addm_prod, addm_ver, tpl_folder

    # noinspection PyBroadException
    def check_hgfs(self, ssh):
        """
        Check if ADDM VM is using mount FS
        If not - will return False (this should trigger usual SFTP upload.)
        If yes -will return args with path mask to remote WORKSPACE (like p4 workspace in local)
        Strange, but I need to regex twice to command result line to allow it to be parsed in the right way!

        This mask will be used to compose paths for each side:

        local                                             - to -  remote:

        workspace                                         - to -  vm_workspace
        d:\perforce\                                      - to -  /usr/tideway/

        CORE_t                                            - to -  vm_CORE_t
        d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE  - to -  /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE


        With command - "df -h"

        Example:
        .host:/utils/                               88G 48G 41G 54% /usr/tideway/utils
        .host:/testutils/                           88G 48G 41G 54% /usr/tideway/python/testutils
        .host:/test_python/                         88G 48G 41G 54% /usr/tideway/TKU/addm/tkn_main/python
        .host:/buildscripts/                        88G 48G 41G 54% /usr/tideway/TKU/addm/tkn_main/buildscripts
        .host:/tku_patterns/CORE/                   88G 48G 41G 54% /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE
        .host:/tku_patterns/SYSTEM/                 88G 48G 41G 54% /usr/tideway/TKU/addm/tkn_main/tku_patterns/SYSTEM
        .host:/DML/                                 88G 48G 41G 54% /usr/tideway/TKU/DML

        Alternative:
        tmpfs           380M     0  380M   0% /run/user/0
        testutils        88G   36G   53G  41% /usr/tideway/python/testutils
        utils            88G   36G   53G  41% /usr/tideway/utils
        perforce         88G   36G   53G  41% /usr/tideway/TKU
        tmpfs           380M     0  380M   0% /run/user/1000


        :return:
        """

        dev_vm_check = False
        vm_dev_path = ''
        err = ''
        try:
            _, stdout, stderr = ssh.exec_command("df -h")
            if stdout:
                output = stdout.readlines()
                for line in output:
                    command_output_parse = self.hgfs_path_re.search(line)
                    if command_output_parse:
                        # Search path to shared folder in all output:
                        path_search = self.vm_tkn_path_re.match(command_output_parse.group(0))
                        if path_search:
                            vm_dev_path = path_search.group('tkn_path')
                            log.debug("<=SHARES=> Addm tkn_path found in VM Ware shares: %s", vm_dev_path)
                            # Stop after any first match is found.
                            break
                    else:
                        alter_shares_check = self.alter_shares_re.findall(line)
                        if alter_shares_check:
                            # This is probably just anu other share mounted, we don't care if path is ok for this:
                            vm_dev_path = '/usr/tideway/TKU'
                            log.debug("<=SHARES=> Addm tkn_path found in other shares: %s", vm_dev_path)
            if stderr:
                err = stderr.readlines()
                if err:
                    raise Exception("ADDM VM command 'df -h' Error:" + str(err))
        except:
            log.error("Error during run 'df -h' command on ADDM!")
            raise Exception("ADDM VM command 'df -h' Error:" + str(err))

        if vm_dev_path:
            dev_vm_check = True
            log.debug("This is probably a dev VM and HGFS share for /addm/tkn_main/tku_patterns/ "
                      "is on place: "+str(vm_dev_path))

        return dev_vm_check, vm_dev_path

    # noinspection PyBroadException
    @staticmethod
    def check_folders(ssh, path):
        """
        Check if folders created, create if needed

        NOTE: I should check_ide this folders in parse_args logic and only if HGFS check_ide = False, so this mean
        that ADDM hasn't shared folders and I should upload data via SFTP

        Folder to check_ide:
        /usr/tideway/TKU/

        If no folder:
        Error: ['ls: cannot access /usr/tideway/XYZ: No such file or directory\n']

        :param ssh:
        :param path: path to check_ide
        """

        folders = []
        ftp = ssh.open_sftp()
        try:
            _, stdout, stderr = ssh.exec_command("ls " + path)
            output_ok = stdout.readlines()
            output_err = stderr.readlines()

            if output_err:
                if "No such file or directory" in output_err[0]:
                    log.debug("Creating folder: " + path)
                    try:
                        ftp.mkdir(path)
                        ftp.mkdir(path+'Tpl_DEV')
                        ssh.exec_command("chmod 777 -R " + path)
                        log.debug("Folder created!")
                    except:
                        log.error("ADDM Folders cannot be created in path: "+str(path))
                else:
                    log.warning("ls command cannot be run on this folder or output is incorrect!")
                    folders = []

            if output_ok:
                for folder in output_ok:
                    folders.append(folder.strip('\n'))
                log.debug("Folder exist! Content: " + ', '.join(folders)+" ls on: "+str(path))
        except:
            log.error("ls command cannot be run on this path: "+str(path))

        return folders

    @staticmethod
    def check_extra_folders(local_cond):
        """

        :return:
        """
        # Get extra folders from previous parse in full_path_args.
        extra_folders = []
        extra_folders_keys = ['BLADE_ENCLOSURE_t',
                              'CLOUD_t',
                              'CORE_t',
                              'DBDETAILS_t',
                              'LOAD_BALANCER_t',
                              'MANAGEMENT_CONTROLLERS_t',
                              'MIDDLEWAREDETAILS_t',
                              'SYSTEM_t',
                              'STORAGE_t']

        # Extracting matched folders from 'local_cond':
        # Making list of all possible pattern paths and then search through them all for imports.
        for folder_key in extra_folders_keys:
            if local_cond[folder_key]:
                extra_folder = local_cond[folder_key]
                # Add only unique folders:
                if extra_folder not in extra_folders:
                    # To be sure I can read files in folder - check_ide folder existence.
                    if os.path.exists(extra_folder) and os.path.isdir(extra_folder):
                        extra_folders.append(extra_folder)
                    else:
                        log.warning("Step 1.1 This path is not exist: "+str(extra_folder))
            else:
                log.info("Be aware that this folder key is not exist: "+str(folder_key))
        return extra_folders

    def get_related_tests(self, **conditions):
        """
        During search of recursive patterns + test, also check_ide each test.py where active pattern also used,
        then compose dict with name of pattern_directory: test_path which will be used for further run to validate
        each related test.

        :return: dict
        """

        local_cond     = conditions['local_cond']
        dev_vm_path    = conditions['dev_vm_path']
        active_pattern = local_cond['file_name']+'.'+local_cond['file_ext']
        workspace      = local_cond['workspace']

        log.debug("Step 1. Search related tests with pattern: "+str(active_pattern))

        # Get extra folders from previous parse in full_path_args.
        extra_folders = self.check_extra_folders(local_cond)

        # Make list of all test.py in extra folders, like in files_to_read()
        exclude_dirs = ['imports'
                        'tpl',
                        'dml',
                        'expected',
                        'actuals',
                        'HarnessFiles']

        # TODO: Is it useful to know which pattern related to each test or not?
        test_files = LocalLogic.tests_to_read(search_path=extra_folders,
                                              exclude_dirs=exclude_dirs,
                                              dev_vm_path=dev_vm_path,
                                              workspace=workspace)
        related_tests = []
        pattern_r = re.compile(active_pattern)
        for test in test_files:
            file = test['test_file']
            local_tests_path = file
            with open(file, "r", encoding="utf8") as f:
                read_file = f.read()

                # pattern_r = re.compile(active_pattern)
                check_modules = pattern_r.findall(read_file)

                # When module name were found in opened file add each to list and later find them:
                if check_modules:
                    # Make dict as  current_modules_name
                    current_pattern_dict = dict(pattern       = active_pattern,
                                                test_path     = local_tests_path,
                                                rem_test_path = test['remote_test_file'],
                                                test_wd       = test['test_wd'],
                                                rem_test_wd   = test['remote_test_wd'])
                    if current_pattern_dict not in related_tests:
                        # Now copy released file:
                        related_tests.append(current_pattern_dict)

        return related_tests

    @staticmethod
    def tests_to_read(search_path, exclude_dirs, dev_vm_path, workspace):
        """
        Read test.py - find pattern load.

        :return:
        """

        file_candidates = []
        # Extra construction for test.py search.
        log.debug("Step 2 - Composing list of all test files in tkn path.")
        # Sort only test.py files
        file_end = "test.py"
        for path in search_path:
            for root, dirs, files in os.walk(path, topdown=True):
                # Exclude service folders:
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                # Make path to each folder:
                for folder in dirs:
                    folder_to_find = os.path.join(root, folder)
                    tests_folder = folder_to_find+os.sep+"tests"
                    # List content of each folder in path and save if there is any file end with tplpre.

                    if os.path.exists(tests_folder):

                        files_in = os.listdir(tests_folder)

                        for file_p in files_in:
                            if file_p.endswith(file_end):
                                # Make full path to tplpre file or files in folder:
                                file_candidate = os.path.join(root, folder)
                                test_file = file_candidate+os.sep+"tests"+os.sep+file_p
                                test_wd = file_candidate+os.sep+"tests"

                                # Replace local workspace path to remote:
                                remote_test_wd = test_wd.replace(workspace, dev_vm_path).replace('\\', '/')
                                remote_test_file = remote_test_wd+'/test.py'

                                if test_file not in file_candidates:
                                    # List with all available pattern files is ready to search with:
                                    file_candidates.append(dict(test_file=test_file,
                                                                test_wd=test_wd,
                                                                remote_test_wd=remote_test_wd,
                                                                remote_test_file=remote_test_file
                                                                ))
                    # Stop on first level, no need to jump deeper.
                    # No need when searching fot test.py:
                    # break
        return file_candidates

