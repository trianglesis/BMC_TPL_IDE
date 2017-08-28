"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import re
import paramiko
from check.local_logic import LocalLogic


class ArgsParse:

    def __init__(self, logging):

        self.logging = logging

        # Checking args for ADDM:
        self.ip_addr_check = re.compile("\d+\.\d+\.\d+\.\d+")  # ip addr
        self.host_name_check = re.compile("\d+\.\d+\.\d+\.\d+")  # when hostname
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
                                'system_user': 'system',
                                'addm_prod': 'Bobblehat',
                                'ssh_connection': <paramiko.client.SSHClient object at 0x00000000035B6CF8>,
                                'disco_mode': 'record',
                                'tpl_vers': '1.13',
                                'dev_vm_check': True,
                                'tpl_folder': 'tpl113',
                                'scan_hosts': '172.25.144.95, 172.25.144.39',
                                'system_password': 'system',
                                'dev_vm_path': '/usr/tideway/TKU'}


        :type known_args: set of args from argsparse
        :return: addm_args_set
        """

        # TODO: Add REST support. Using known args - decide which auth to use REST or SSH.

        log = self.logging
        addm_env_check = LocalLogic(log)

        addm_host = known_args.addm_host
        user = known_args.user
        password = known_args.password
        disco_mode = known_args.disco_mode
        scan_host_list = known_args.scan_host_list

        # For user 'system' in addm - which is used to start scans,, activate patterns, etc.
        system_user = known_args.system_user
        if not system_user:
            system_user = 'system'
        system_password = known_args.system_password
        if not system_password:
            system_password = 'system'

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
            tpl_vers, addm_prod, addm_ver, tpl_folder = addm_env_check.check_addm_tpl_ver(ssh)

            '''
            If result of dev_vm_check is True - there will be a string with path to 'dev_vm_check': '/usr/tideway/TKU'
            And then I can compose any needed paths to files from local to remote. More in check_hgfs() - doc.
            If not - it will bool False and before starting upload I will check this and if it False - 
                SFTP upload will be started, or REST - for the future upgrades of this code.
            '''
            dev_vm_check, dev_vm_path = addm_env_check.check_hgfs(ssh)

            tku_dev_path = '/usr/tideway/TKU/'
            if not dev_vm_check:
                '''
                   This path should be the same for all DEV VMs to be sure the logic will find it on expected place.
                   If this path is changing - it should be changed everywhere for all users who use this program.
                '''
                folders = addm_env_check.check_folders(ssh, tku_dev_path)
                for folder in folders:
                    if "addm" in folder:
                        dev_vm_path = tku_dev_path
                        log.debug("Development path is found on this ADDM and "
                                  "will be used for upload patterns and tests.")

        else:
            log.info("SSH connection to ADDM was not established! Other arguments of SCAN will be ignored.")

        addm_args_set = dict(ssh_connection  = ssh,
                             disco_mode      = disco,
                             system_password = system_password,
                             system_user     = system_user,
                             scan_hosts      = scan_hosts,
                             addm_ver        = addm_ver,
                             tpl_vers        = tpl_vers,
                             tpl_folder      = tpl_folder,
                             dev_vm_check    = dev_vm_check,
                             dev_vm_path     = dev_vm_path,
                             addm_prod       = addm_prod)
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

        Disabling to allow use host names:
        check = self.ip_addr_check.match(addm_host)
        if check:
            addm_host = addm_host  # ADDM ip is:                192.168.5.6

        :param password: str
        :param user: str
        :param addm_host: str
        """
        log = self.logging

        ssh = ''
        if addm_host:

            if user:
                pass
            else:
                log.error("Please specify user name!")
            # password = ''
            if password:
                pass
            else:
                log.error("Your ADDM password is empty!")

            log.info("INFO: ADDM host is: " + addm_host)
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
                    log.critical("Connection failed. Probably host or IP of ADDM is not set or incorrect!")
                    log.warn("Will continue further check, but nothing will proceed on ADDM!")
                    ssh = False
                    # raise
            else:
                log.error("There is no ADDM user and password found in args! I cannot connect ADDM.")
        else:
            log.info("There is no ADDM IP or host found in args!")

        return ssh

    def discovery_mode_check(self, disco_mode):
        """
        Check the discovery mode to run discovery
         (standard|playback|record)
         Should run only if SSH session established!
        """
        log = self.logging

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

        :param host_list_arg: str
        """
        log = self.logging
        host_list = False

        if host_list_arg:
            check = self.ip_addr_check.match(host_list_arg)
            if check:
                host_list = host_list_arg  # Host(s) to scan are:       10.49.32.114
                log.debug("Will add host(s) for discovery: " + str(host_list))
            else:
                log.warn("Host list for scan should consist of IPs.")
        else:
            if host_list != 'None':
                log.info("Please specify some hosts to scan for ADDM!")
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

        recursive_imports = False
        usual_imports = False
        read_test = False
        oper_args_set = {
            'recursive_imports': recursive_imports,
            'usual_imports': usual_imports,
            'read_test': read_test,
        }

        if known_args.read_test and known_args.recursive_import:
            read_test = True
            recursive_imports = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        elif known_args.usual_import and not known_args.recursive_import:
            usual_imports = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        elif known_args.recursive_import and not known_args.usual_import:
            recursive_imports = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        elif known_args.usual_import and known_args.recursive_import:
            log.warn("You cannot add two import scenarios in one run. Please choose only one. "
                     "But I will run usual_imports by default.")
            usual_imports = True
            oper_args_set = {
                'recursive_imports': recursive_imports,
                'usual_imports': usual_imports,
                'read_test': read_test,
            }

        return oper_args_set
