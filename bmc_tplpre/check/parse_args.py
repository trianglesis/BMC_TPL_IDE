"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import re
import os
import paramiko
from check.local_logic import LocalLogic

# DEBUG
import json
from pprint import pformat

class ArgsParse:

    def __init__(self, logging):

        self.logging = logging

        # TPL versions check:
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
                                 '11.2': 'CustardCream',
                                 '11.1': 'Bobblehat',
                                 '11.0': 'Aardvark',
                                 '10.2': 'Zythum',
                                 '10.1': 'Zed',
                                 '10.0': 'Yodel'
                                 }

        self.TPL_VERSIONS = {
                             'CustardCream':     '1.14',
                             'Bobblehat':        '1.13',
                             'Aardvark':         '1.12',
                             'Zythum':           '1.10',
                             'Zed':              '1.9',
                             'Yodel':            '1.8'
                             }

        # Checking args for ADDM:
        self.ip_addr_check = re.compile("\d+\.\d+\.\d+\.\d+")  # ip addr
        self.disco_mode_check = re.compile("standard|playback|record")  # standard|playback|record

        # Parsing ADDM version:
        # BMC Discovery Version: 11.1.0.5 Release: 698363
        self.addm_version_full_re = re.compile("BMC\sDiscovery\sVersion:\s+(\d+(?:\.\d+)*)")
        self.addm_version_re = re.compile("^(\d+(?:\.\d+)?)")

        # HGFS ADDM folder shares check
        self.hgfs_path_re = re.compile("(?P<tkn_path>\S+)/addm/tkn_main/tku_patterns/(?:CORE|DBDETAILS|MANAGEMENT_CONTROLLERS|MIDDLEWAREDETAILS)")
        self.vm_tkn_path_re = re.compile("(?P<tkn_path>\S+)/addm/tkn_main/tku_patterns/")

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
        log = self.logging

        # Args dedicated to local paths from full path extracted:
        local_arguments_set = self.full_path_parse(known_args.full_path)

        # Args dedicated to imports logic from args parse:
        operational_args_set = self.operational_mode_check(known_args)

        # Args dedicated to addm actions - gathered from addm ssh connection if available:
        addm_args_set = self.addm_args(known_args)

        if extra_args:
            log.warn("HEY, you forgot some arguments:" + str(extra_args))

        return local_arguments_set, operational_args_set, addm_args_set

    def addm_args(self, known_args):
        """
        Get SSH <paramiko.client.SSHClient object at 0x00000000035DADD8>

        Check usual arguments to compose then dict with everything I need to continue work.
        Most of checks should be finished here, so further I'll have just a set of args to use in globallogic.

        Return set of options: {'addm_ver': '11.1',
                                'disco_mode': 'record',
                                'scan_hosts': '1.1.1.1, 2.2.2.2, 3.3.3.3',
                                'addm_prod': 'Bobblehat',
                                'tpl_vers': '1.13',
                                'ssh_connection': <paramiko.client.SSHClient object at 0x00000000035DADD8>}

        :type known_args: set of args from argsparse
        :return: addm_args_set
        """
        # TODO: Add REST support. Using known args - decide which auth to use REST or SSH.

        log = self.logging

        addm_host = known_args.addm_host
        user = known_args.user
        password = known_args.password
        disco_mode = known_args.disco_mode
        scan_host_list = known_args.scan_host_list

        tpl_vers = ''
        addm_ver = ''
        tpl_folder = ''
        addm_prod = ''

        dev_vm_path = False
        dev_vm_check = False

        disco = self.discovery_mode_check(disco_mode)
        scan_hosts = self.host_list_check(scan_host_list)

        ssh = self.addm_host_check(addm_host, user, password)
        if ssh:
            '''
            Here I check ADDM VM version and tpl version supported.
            If ADDM connection is established - run versioning command and compare its result with 
            version table to obtain latest supported tpl code version to upload.
            More in check_addm_tpl_ver() doc.
            '''
            tpl_vers, addm_prod, addm_ver, tpl_folder = self.check_addm_tpl_ver(ssh)

            '''
            If result of dev_vm_check is True - there will be a string with path to 'dev_vm_check': '/usr/tideway/TKU'
            And then I can compose any needed paths to files from local to remote. More in check_hgfs() - doc.
            If not - it will bool False and before starting upload I will check this and if it False - 
                SFTP upload will be started, or REST - for the future upgrades of this code.
            '''
            dev_vm_check, dev_vm_path = self.check_hgfs(ssh)

            tku_dev_path = '/usr/tideway/TKU/'
            if not dev_vm_check:
                '''
                   This path should be the same for all DEV VMs to be sure the logic will find it on expected place.
                   If this path is changing - it should be changed everywhere for all users who use this programm.
                '''
                folders = self.check_folders(ssh, tku_dev_path)
                for folder in folders:
                    if "addm" in folder:
                        dev_vm_path = tku_dev_path
                        log.debug("Development path is found on this ADDM and "
                                  "will be used for upload patterns and tests.")

        else:
            log.warn("SSH connection to ADDM was not established! Other arguments of SCAN will be ignored.")

        addm_args_set = {'ssh_connection': ssh,
                         'disco_mode': disco,
                         'scan_hosts': scan_hosts,
                         'addm_ver': addm_ver,
                         'tpl_vers': tpl_vers,
                         'tpl_folder': tpl_folder,
                         'dev_vm_check': dev_vm_check,
                         'dev_vm_path': dev_vm_path,
                         'addm_prod': addm_prod}

        return addm_args_set

    def full_path_parse(self, full_path):
        """
        Input the full path arg and tries to parse it for further usage in different scenarios:

        Example 1:
        - When full path if for PATTEN (tpl or TPLPRE)
            d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\BMCRemedyARSystem.tplpre
            d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\tpl110\BMCRemedyARSystem.tpl


        Output: dictionary with configured arguments for further usage.

        :param full_path: str
        :return: dict
        """


        log = self.logging
        path_logic = LocalLogic(log)
        args = path_logic.file_path_decisions(full_file_path=full_path)

        return args

    def addm_host_check(self, addm_host, user, password):
        """
        Check login and password for provided ADDM IP
        If no ADDM IP - should not run this and upload, disco.
        Check ADDM host IP where to upload and scan
        Should checked at first - before upload, scan, disco

        :param password: str
        :param user: str
        :param addm_host: str
        """
        # TODO: Ability to use addm hostname.
        # TODO: Add pass for system user.

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

        ssh = ''
        if addm_host:
            check = self.ip_addr_check.match(addm_host)
            if check:
                addm_host = addm_host  # ADDM ip is:                192.168.5.6
                log.info("INFO: ADDM ip is: " + addm_host)
                # Open SSH session if ADDM IP and USER and PASSWORD are present
                if user and password:
                    log.debug("Trying to connect ADDM " + addm_host + " via SSH as user: " + user)
                    ssh = paramiko.SSHClient()  # Start the session with ADDM machine:
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        ssh.connect(addm_host, username=user, password=password)
                    except paramiko.ssh_exception.AuthenticationException:
                        log.error("Authentication failed with ADDM")
                        ssh = False
                    except TimeoutError:
                        log.critical("Connection failed. Probably IP of ADDM is not set or incorrect!")
                        log.warn("Will continue further check, but nothing will proceed on ADDM!")
                        ssh = False
                        # raise
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

    def host_list_check(self, host_list_arg):
        """
        Check host list before start scan
        Will add hostname support maybe
        Should run only if SSH session established!
        :param host_list:
        """
        # TODO: add Ability to use hostnames.
        log = self.logging
        # HOSTs ip check:NoneNone
        # host_list = ''

        if host_list_arg:
            check = self.ip_addr_check.match(host_list_arg)
            if check:
                host_list = host_list_arg  # Host(s) to scan are:       10.49.32.114
                log.debug("Will add host(s) for discovery with IP: " + str(host_list))
        else:
            host_list = False
            if host_list != 'None':
                log.error("Please specify some hosts to scan for ADDM!")
            else:
                log.info("Pattern upload only. No host added for Discovery run!")

        return host_list

    def operational_mode_check(self, known_args):
        """
        Dict should not be empty even if there is no args for that.
        Further Ill check and use logic.
        Vars should be re-written of True:

        :param known_args:
        :return: dict of Bool actions
        """
        log = self.logging

        # TODO: Args rename:
        recursive_imports = False
        usual_imports = False
        read_test = False
        oper_args_set = {
            'recursive_imports': recursive_imports,
            'usual_imports': usual_imports,
            'read_test': read_test,
        }

        if known_args.T:
            read_test = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        if known_args.imp:
            usual_imports = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        if known_args.r_imp:
            recursive_imports = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        if known_args.imp and known_args.r_imp:
            log.warn("You cannot add two import scenarios in one run. Please choose one only.")

        return oper_args_set

    def check_addm_tpl_ver(self, ssh):
        """
        Run command "tw_pattern_management -v"
        Parse version and compare with version dict.
        :param ssh:
        :return:
        """
        log = self.logging
        tpl_vers = ''
        addm_prod = ''
        addm_ver = ''
        tpl_folder = ''

        _, stdout, stderr = ssh.exec_command("tw_pattern_management -v")
        if stdout:

            output = stdout.readlines()
            addm_version_full = self.addm_version_full_re.match(output[0])
            addm_version = self.addm_version_re.match(addm_version_full.group(1))
            addm_ver = str(addm_version.group(1))

            # print(output)
            if addm_ver in self.PRODUCT_VERSIONS:
                addm_prod = self.PRODUCT_VERSIONS[addm_ver]
                tpl_vers = self.TPL_VERSIONS[addm_prod]
                if tpl_vers in self.tpl_folder_k:
                    tpl_folder = self.tpl_folder_k[tpl_vers]

                # print(tpl_vers)
        if stderr:
            err = stderr.readlines()
            if err:
                log.warn("ADDM versioning command fails with error: " + str(err))

        return tpl_vers, addm_prod, addm_ver, tpl_folder

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


        https://confluence.bmc.com/display/~odanylch/ADDM+VM+Image+settings

        :return:
        """
        log = self.logging

        # TODO: ../TKU/.. folder should somehow documented as really MUSTHAVE parameter in ane ENV.
        dev_vm_check = False
        vm_dev_path = ''
        _, stdout, stderr = ssh.exec_command("df -h")
        if stdout:
            output = stdout.readlines()
            for line in output:
                command_output_parse = self.hgfs_path_re.search(line)
                if command_output_parse:
                    path_search = self.vm_tkn_path_re.match(command_output_parse.group(0))
                    if path_search:
                        vm_dev_path = path_search.group('tkn_path')
                        # Stop after any first match is found.
                        break
        if stderr:
            err = stderr.readlines()
            if err:
                print(err)

        if vm_dev_path:
            dev_vm_check = True
            log.debug("This is probably a dev VM and HGFS share for /addm/tkn_main/tku_patterns/ "
                      "is on place: "+str(vm_dev_path))

        return dev_vm_check, vm_dev_path

    def check_folders(self, ssh, path):
        """
        Check if folders created, create if needed

        NOTE: I should check this folders in parse_args logic and only if HGFS check = False, so this mean
        that ADDM hasn't shared folders and I should upload data via SFTP

        Folder to check:
        /usr/tideway/TKU/

        If no folder:
        Error: ['ls: cannot access /usr/tideway/XYZ: No such file or directory\n']

        :param ssh:
        :param path: path to check
        """
        # TODO: Check if tideway user can run this.
        # TODO: Create all needed dev folders here.
        # TODO: MOve it from here or not?

        log = self.logging

        folders = []
        ftp = ssh.open_sftp()
        _, stdout, stderr = ssh.exec_command("ls " + path)
        output_ok = stdout.readlines()
        output_err = stderr.readlines()
        if output_err:
            if "No such file or directory" in output_err[0]:
                log.debug("Creating folder: " + path)
                ftp.mkdir(path)
                ftp.mkdir(path+'Tpl_DEV')
                ssh.exec_command("chmod 777 -R " + path)
                log.debug("Folder created!")
            else:
                log.warn("ls command cannot be run on this folder or output is incorrect!")
                folders = []

        if output_ok:
            for folder in output_ok:
                folders.append(folder.strip('\n'))
            log.debug("Folder exist! Content: " + ', '.join(folders)+" ls on: "+str(path))

        return folders