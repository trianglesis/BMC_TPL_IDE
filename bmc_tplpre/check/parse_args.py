import re
import os
import paramiko


class ArgsParse:

    def __init__(self, logging):

        self.logging = logging

        # Checking psth for useful arguments:
        self.dev_path_re = re.compile('(\S+)(\\\\addm\\\\tkn_main\\\\tku_patterns\\\\)')

        self.workspace_rs      = '(?P<workspace>\S+)'
        self.addm_rs           = '(?P<addm>addm)'
        self.tkn_main_rs       = '(?P<tkn_main>tkn_main)'
        self.tku_patterns_rs   = '(?P<tku_patterns>tku_patterns)'
        self.pattern_lib_rs    = '(?P<pattern_lib>[^\\\\]+)'

        self.pattern_folder_rs = '(?P<pattern_folder>[^\\\\]+)'

        self.tpl_folder_rs     = '(?P<tpl_folder>tpl\d+)'
        self.file_name_rs      = '(?P<file_name>\S+)\.'
        self.file_ext_rs       = '(?P<file_ext>\S+)'

        self.win_esc = '\\\\'

        # Composing different REGEX strings to get args for different types of files in path.
        # (?P<workspace>\S+)\\(?P<addm>addm)\\(?P<tkn_main>tkn_main)\\(?P<tku_patterns>tku_patterns)\\(?P<pattern_lib>[^\\]+)\\(?P<pattern_folder>[^\\]+)\\(?P<file_name>\S+)\.(?P<file_ext>\S+)
        self.path_parse_re = re.compile(self.workspace_rs      + self.win_esc +
                                        self.addm_rs           + self.win_esc +
                                        self.tkn_main_rs       + self.win_esc +
                                        self.tku_patterns_rs   + self.win_esc +
                                        self.pattern_lib_rs    + self.win_esc +
                                        self.pattern_folder_rs + self.win_esc +
                                        self.file_name_rs      + self.file_ext_rs)

        # (?P<workspace>\S+)\\(?P<addm>addm)\\(?P<tkn_main>tkn_main)\\(?P<tku_patterns>tku_patterns)\\(?P<pattern_lib>[^\\]+)\\(?P<pattern_folder>[^\\]+)\\(?P<tpl_folder>tpl\d+)\\(?P<file_name>\S+)\.(?P<file_ext>\S+)
        self.tpl_path_parse_re = re.compile(self.workspace_rs      + self.win_esc +
                                            self.addm_rs           + self.win_esc +
                                            self.tkn_main_rs       + self.win_esc +
                                            self.tku_patterns_rs   + self.win_esc +
                                            self.pattern_lib_rs    + self.win_esc +
                                            self.pattern_folder_rs + self.win_esc +
                                            self.tpl_folder_rs     + self.win_esc +
                                            self.file_name_rs      + self.file_ext_rs)

        self.alone_pattern_re = re.compile('([^"]+)\.(tplpre|tpl)')

        self.alone_tplpre_re = re.compile(self.pattern_folder_rs + self.win_esc +
                                          self.file_name_rs      + '(?P<file_ext>tplpre)')

        self.alone_tpl_re = re.compile(self.pattern_folder_rs + self.win_esc +
                                       self.file_name_rs      + '(?P<file_ext>tpl)')

        self.tpl_ver_check = re.compile("\d+\.\d+")  # TPl ver 10.2,11.0...
        self.tpl_folder_k = {'8.3': 'tpl16',
                             '9.0': 'tpl17',
                             '10.0': 'tpl18',
                             '10.1': 'tpl19',
                             '10.2': 'tpl110',
                             '11.2': 'tpl112',
                             '11.3': 'tpl113',
                             '11.4': 'tpl114'
                             }

        # Checking args for ADDM:
        self.ip_addr_check = re.compile("\d+\.\d+\.\d+\.\d+")  # ip addr
        self.disco_mode_check = re.compile("standard|playback|record")  # standard|playback|record

    def gather_args(self, known_args, extra_args):
        """
        Proceed incoming arguments into key-value dict and return for further usage.
        Working to get info only for files and paths args:
        Example: {'workspace': 'd:\\perforce', 'file_ext': 'tpl',
                  'pattern_lib': 'CORE', 'file_name': 'BMCRemedyARSystem',
                  'pattern_folder': 'BMCRemedyARSystem', 'working_dir': 'tpl114',
                  'addm': 'addm', 'tku_patterns': 'tku_patterns', 'tkn_main': 'tkn_main'}

        :return:
        """
        # print(known_args)
        # print(extra_args)

        full_path_args = self.full_path_parse(known_args.full_path)

        return full_path_args

    def addm_args(self, known_args, extra_args):
        """
        Proceed incoming args into key-value dict and return for further usage.
        Working to get info only for ADDM machine usage, like: addm ip, scan ip, disco mode, tpl version

        Will try to return ssh console and set of options to run.
        :return:
        """

        addm_host = known_args.addm_host
        user = known_args.user
        password = known_args.password
        disco_mode = known_args.disco_mode
        scan_host_list = known_args.scan_host_list

        ssh = self.addm_host_check(addm_host, user, password)
        disco = self.discovery_mode_check(disco_mode)
        scan_hosts = self.host_list_check(scan_host_list)

        return ssh, disco, scan_hosts

    # TODO To be disabled:
    def tpl_version_check(self, tpl_ver):
        """
            if argument "-tpl", "--TPL_Version" is set - will try to check it's format and version. Then will compose
            path to folder where TPLPreprocessor should output for current version:
            - at first will run syntax check with this version (tplint)
            - will try to check if folder for this version was created after Tplpreproc

            If no argument set - will WARN and pass this and return None

            (Discovery/TPL versions: 8.3(1.6) 9.0(1.7) 10.0(1.8) 10.1(1.9) 10.2(1.10) 11.0(1.11))
            :param log:
            :param tpl_ver: str

            :return: tpl_folder, tpl_version
            """

        tpl_version = ''
        tpl_folder = ''
        log = self.logging

        if tpl_ver:
            check = self.tpl_ver_check.match(tpl_ver)
            if check:
                tpl_version = tpl_ver
                if tpl_ver in self.tpl_folder_k:
                    tpl_folder = self.tpl_folder_k[tpl_ver]
                else:
                    log.error("TPL version is incorrect: " + tpl_ver +
                              "! Please specify correct tpl version! \nDiscovery/TPL versions: "
                              "8.3(1.6) 9.0(1.7) 10.0(1.8) 10.1(1.9) 10.2(1.10) 11.0(1.11)")
                log.info("TPL version: " + tpl_ver)
                log.info("TPL tpl_folder: " + tpl_folder)
            else:
                log.warn("If no TPL Version (--tpl arg) then upload will be started "
                         "with current file! \n"
                         "No Tplpreproc and no syntax check will started!")
        else:
            log.warn("If no TPL Version (--tpl arg) then upload will be started "
                     "with current file! \n"
                     "No Tplpreproc and no syntax check will started!")

        return tpl_folder, tpl_version

    def full_path_parse(self, full_path):
        """
        Input the full path arg and tries to parse it for further usage in different scenarios:

        Example 1:
        - When full path if for PATTEN (tpl or TPLPRE)
            d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\BMCRemedyARSystem.tplpre
            d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\tpl110\BMCRemedyARSystem.tpl


        Output: dictionary with configured arguments for further usage.
        Arguments from file path: {'file_name': 'BMCRemedyARSystem',
                                   'pattern_folder': 'BMCRemedyARSystem',
                                   'tku_patterns': 'tku_patterns',
                                   'tkn_main': 'tkn_main',
                                   'workspace': 'd:\\perforce\\',
                                   'file_ext': 'tplpre',
                                   'pattern_lib': 'CORE',
                                   'addm': 'addm'}

        :param full_path:
        :return:
        """
        log = self.logging

        if full_path:
            log.info("-full_path is: " + full_path)
            # Checking for different paths logic
            dev_path_check = self.dev_path_re.match(full_path)

            # Check path as typical DEV tree:
            # Should match 'd:\perforce\addm\tkn_main\tku_patterns'
            if dev_path_check:
                log.debug("This is dev path.")

                # Check full arguments:
                path_parse = self.path_parse_re.match(full_path)
                if path_parse:
                    log.debug("Parsing path for options.")

                    workspace      = path_parse.group('workspace')
                    addm           = path_parse.group('addm')
                    tkn_main       = path_parse.group('tkn_main')
                    tku_patterns   = path_parse.group('tku_patterns')
                    pattern_lib    = path_parse.group('pattern_lib')
                    pattern_folder = path_parse.group('pattern_folder')
                    file_name      = path_parse.group('file_name')
                    file_ext       = path_parse.group('file_ext')

                    # Check if this is a tplpre file from: PatternFolder\PatternName.tplpre
                    if re.match('tplpre', file_ext):

                        # TODO: Experimental - probably better to use -wd in other way
                        # Composing working dir to allow syntax check for all content in folder.
                        # More obvious to use values from regex rather then just strings.
                        working_dir = workspace     + os.sep + \
                                      addm          + os.sep + \
                                      tkn_main      + os.sep + \
                                      tku_patterns  + os.sep + \
                                      pattern_lib   + os.sep + \
                                      pattern_folder

                        args_dict = {'workspace': workspace,
                                     'addm': addm,
                                     'tkn_main': tkn_main,
                                     'tku_patterns': tku_patterns,
                                     'pattern_lib': pattern_lib,
                                     'pattern_folder': pattern_folder,
                                     'file_name': file_name,
                                     'file_ext': file_ext,
                                     'working_dir': working_dir}
                        log.info("Arguments from file path: " + str(args_dict))
                        return args_dict

                    # Check if this is a tpl file from: PatternFolder\tpl110\PatternName.tpl
                    elif re.match('tpl', file_ext):
                        log.debug("File extension matched tpl pattern.")

                        path_parse = self.tpl_path_parse_re.match(full_path)
                        pattern_folder = path_parse.group('pattern_folder')
                        file_name      = path_parse.group('file_name')
                        file_ext       = path_parse.group('file_ext')
                        tpl_folder     = path_parse.group('tpl_folder')

                        args_dict = {'workspace': workspace,
                                     'addm': addm,
                                     'tkn_main': tkn_main,
                                     'tku_patterns': tku_patterns,
                                     'pattern_lib': pattern_lib,
                                     'pattern_folder': pattern_folder,
                                     'file_name': file_name,
                                     'file_ext': file_ext,
                                     'working_dir': tpl_folder}
                        log.info("Arguments from file path: " + str(args_dict))
                        return args_dict

                    # Check if this is a dml file from: ..\tests\dml\DML_DATA.dml
                    elif re.match('dml', file_ext):
                        log.debug("This is DML file.")
                        args_dict = {'workspace': workspace,
                                     'addm': addm,
                                     'tkn_main': tkn_main,
                                     'tku_patterns': tku_patterns,
                                     'pattern_lib': pattern_lib,
                                     'pattern_folder': pattern_folder,
                                     'file_name': file_name,
                                     'file_ext': file_ext,
                                     'working_dir': ''}
                        log.info("Arguments from file path: " + str(args_dict))
                        return args_dict

                    # Check if this is a model file from: \tests\actuals\SI_MODEL.model
                    # TODO: Fix 'file_name': 'tests\\expected\\test10_Unix_ARSystem90'
                    elif re.match('model', file_ext):
                        log.debug("This is model file.")
                        args_dict = {'workspace': workspace,
                                     'addm': addm,
                                     'tkn_main': tkn_main,
                                     'tku_patterns': tku_patterns,
                                     'pattern_lib': pattern_lib,
                                     'pattern_folder': pattern_folder,
                                     'file_name': file_name,
                                     'file_ext': file_ext,
                                     'working_dir': ''}
                        log.info("Arguments from file path: " + str(args_dict))
                        return args_dict

                    # Check if this is a py file from: ..\tests\test.py
                    elif re.match('py', file_ext):
                        log.debug("This is py file. Will check if this is a 'test.py'")
                        args_dict = {'workspace': workspace,
                                     'addm': addm,
                                     'tkn_main': tkn_main,
                                     'tku_patterns': tku_patterns,
                                     'pattern_lib': pattern_lib,
                                     'pattern_folder': pattern_folder,
                                     'file_name': file_name,
                                     'file_ext': file_ext,
                                     'working_dir': ''}
                        log.info("Arguments from file path: " + str(args_dict))
                        return args_dict

                    # If this file has an extension I do not support:
                    else:
                        log.warn("Did not match any file extension "
                                 "I can use: 'tpl', 'tplpre', 'dml', 'model', 'test.py'")
                    log.debug("Path matched and parsed.")
                else:
                    log.warn("Did not match TKU DEV pattern path tree! Will use another way to parse.")
                    log.debug("I expect path to file: d:\\P4\\addm\\tkn_main\\tku_patterns\\..\\..\\FileName.Ext")

            # When path to file has no tku_tree in. This is probably standalone file from anywhere.
            else:
                log.debug('There is no dev path in -full_path - I expect "..\\addm\\tkn_main\\tku_patterns\\.."\n '
                          'Trying to locate place for alone pattern file.')

                # To be sure I have here - is a pattern file with tpl or tplre ext.
                # Also checking full path to file. No spaces or extra sumbols allowed.
                alone_pattern_check = self.alone_pattern_re.match(full_path)
                if alone_pattern_check:
                    alone_tplpre_check = self.alone_tplpre_re.match(full_path)
                    # Sort tplpre:
                    if alone_tplpre_check:
                        pattern_folder = alone_tplpre_check.group('pattern_folder')
                        file_name      = alone_tplpre_check.group('file_name')
                        file_ext       = alone_tplpre_check.group('file_ext')
                        log.debug("This is alone tplpre file - will use path 'as is' "
                                  "To run TPLPreproc or Syntax check - p4_path should be configured.")
                        args_dict = {'workspace': '',
                                     'addm': '',
                                     'tkn_main': '',
                                     'tku_patterns': '',
                                     'pattern_lib': '',
                                     'pattern_folder': pattern_folder,
                                     'file_name': file_name,
                                     'file_ext': file_ext}
                    # If not *.tlpre
                    else:
                        alone_tpl_check = self.alone_tpl_re.match(full_path)
                        # But then check I have a proper *.tpl
                        if alone_tpl_check:
                            pattern_folder = alone_tpl_check.group('pattern_folder')
                            file_name      = alone_tpl_check.group('file_name')
                            file_ext       = alone_tpl_check.group('file_ext')
                            log.debug("This is alone tpl file - will use path 'as is'."
                                      "Upload to ADDM and scan could be started if arguments was set.")
                            args_dict = {'workspace': '',
                                         'addm': '',
                                         'tkn_main': '',
                                         'tku_patterns': '',
                                         'pattern_lib': '',
                                         'pattern_folder': pattern_folder,
                                         'file_name': file_name,
                                         'file_ext': file_ext}
                        else:
                            log.warn("This path did not match any suitable pattern and probably not a tpl file"
                                     " Or path has superfluous symbols or spaces")
                else:
                    log.debug("Cannot match file path for alone pattern. "
                              "I expect: d:\\Something\\SomePattern.(tpl|tplpre)")

        else:
            log.warn("No '-full_path' argument was set.")

    def addm_host_check(self, addm_host, user, password):
        """
        Check login and password for provided ADDM IP
        If no ADDM IP - should not run this and upload, disco.
        Check ADDM host IP where to upload and scan
        Should checked at first - before upload, scan, disco

        :param log:
        :param password: str
        :param user: str
        :param addm_host: str
        """

        log = self.logging
        # user = ''

        if user:
            pass
        else:
            log.error("Please specify user name!")
        # password = ''
        if password:
            pass
        else:
            log.error("Your ADDM password is empty!")

        # addm_host = '' # check ADDM_HOST ip
        ssh = ''
        if addm_host:
            check = self.ip_addr_check.match(addm_host)
            if check:
                addm_host = addm_host  # ADDM ip is:                192.168.5.6
                log.info("INFO: ADDM ip is:" + " " * 47 + addm_host)
                # Open SSH session if ADDM IP and USER and PASSWORD are present
                if user and password:
                    ssh = paramiko.SSHClient()  # Start the session with ADDM machine:
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        ssh.connect(addm_host, username=user, password=password)
                    except paramiko.ssh_exception.AuthenticationException:
                        log.error("Authentication failed with ADDM")
                        ssh = False
                else:
                    log.error("There is no ADDM ip in args found or TPL preproc did not run.")
            else:
                log.error("Please specify correct ADDM IP format: '\d+\.\d+\.\d+\.\d+' !")
        else:
            log.warn("WARN: There is no ADDM IP found in args!")

        return ssh

    def discovery_mode_check(self, disco_mode):
        """
        Check the discovery mode to run discovery
         (standard|playback|record)
         Should run only if SSH session established!
        """
        log = self.logging
        # disco_mode = '' # check discovery mode

        if disco_mode:
            check = self.disco_mode_check.match(disco_mode)
            if check:
                disco_mode = disco_mode  # Discovery mode is:         standard
                log.info("Discovery mode is: " + str(disco_mode))
        else:
            log.info("Discovery mode not set or not used.")

        return disco_mode

    def host_list_check(self, host_list):
        """
        Check host list before start scan
        Will add hostname support maybe
        Should run only if SSH session established!
        :param log:
        :param host_list:
        """
        log = self.logging
        # HOSTs ip check:NoneNone
        # host_list = ''

        if host_list:
            check = self.ip_addr_check.match(host_list)
            if check:
                host_list = host_list  # Host(s) to scan are:       10.49.32.114
                log.debug("Will add host(s) for discovery with IP: " + str(host_list))
        else:
            host_list = False
            if host_list != 'None':
                log.error("Please specify some hosts to scan for ADDM!")
            else:
                log.info("Pattern upload only. No host added for Discovery run!")

        return host_list
