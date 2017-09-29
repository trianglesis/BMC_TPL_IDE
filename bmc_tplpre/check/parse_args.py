"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import re
import paramiko
from check.local_logic import LocalLogic
import logging

log = logging.getLogger("check.logger")


class ArgsParse:

    def __init__(self):

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

        # Args dedicated to local paths from full path extracted:
        local_args_set = self.full_path_parse(known_args.full_path)
        assert isinstance(local_args_set, dict)

        # Args dedicated to imports logic from args parse:
        oper_args_set = self.oper_mode(known_args)
        assert isinstance(oper_args_set, dict)

        # Args dedicated to addm actions - gathered from addm ssh connection if available:
        addm_args_set = self.addm_args(known_args)
        assert isinstance(addm_args_set, dict)

        if extra_args:
            log.warning("HEY, you forgot some arguments:" + str(extra_args))

        return local_args_set, oper_args_set, addm_args_set

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

        addm_env_check = LocalLogic()

        addm_host      = known_args.addm_host
        user           = known_args.user
        password       = known_args.password
        disco_mode     = known_args.disco_mode
        scan_host_list = known_args.scan_host_list

        # For user 'system' in addm - which is used to start scans,, activate patterns, etc.
        system_user = known_args.system_user
        if not system_user:
            system_user = 'system'
        system_password = known_args.system_password
        if not system_password:
            system_password = 'system'

        tpl_vers     = ''
        addm_ver     = ''
        tpl_folder   = ''
        addm_prod    = ''

        dev_vm_path  = False
        dev_vm_check = False

        disco        = self.discovery_mode_check(disco_mode)
        scan_hosts   = self.host_list_check(scan_host_list)

        ssh          = self.addm_host_check(addm_host, user, password)
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

    @staticmethod
    def full_path_parse(full_path):
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

        path_logic = LocalLogic()
        args = path_logic.file_path_decisions(full_file_path=full_path)

        return args

    @staticmethod
    def addm_host_check(addm_host, user, password):
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

            log.info("ADDM host: " + addm_host)
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
                    log.warning("Will continue further check, but nothing will proceed on ADDM!")
                    ssh = False
                    # raise
            else:
                log.error("There is no ADDM user and password found in args! I cannot connect ADDM.")

        return ssh

    def discovery_mode_check(self, disco_mode):
        """
        Check the discovery mode to run discovery
         (standard|playback|record)
         Should run only if SSH session established!
        """

        if disco_mode:
            check = self.disco_mode_check.match(disco_mode)
            if check:
                disco_mode = disco_mode  # Discovery mode is:         standard
                log.info("Discovery mode: " + str(disco_mode))

        return disco_mode

    def host_list_check(self, host_list_arg):
        """
        Check host list before start scan
        Will add hostname support maybe
        Should run only if SSH session established!

        :param host_list_arg: str
        """
        host_list = False

        if host_list_arg:
            check = self.ip_addr_check.match(host_list_arg)
            if check:
                host_list = host_list_arg  # Host(s) to scan are:       10.49.32.114
                log.debug("Will add host(s) for discovery: " + str(host_list))
            else:
                log.warning("Host list for scan should consist of IPs.")
        else:
            if host_list != 'None':
                pass
            else:
                log.info("Pattern upload only.")

        return host_list

    @staticmethod
    def oper_mode(known_args):
        """
        Dict should not be empty even if there is no args for that.
        Further Ill check and use logic.
        If imports used - than no test run!
        I test run used - than no imports!

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

        :param known_args:
        :return: dict of Bool actions
        """

        oper_args_set = dict(
                             imports = dict(recursive_imports=False,
                                            usual_imports=False,
                                            read_test=False),
                             tests = dict(related_tests=False,
                                          run_test=False,
                                          test_verbose=False,
                                          test_failfast=False
                                          ),
                             tku_oper = dict(wipe_tku=False)
                             )

        if known_args.read_test and known_args.recursive_import:
            oper_args_set['imports']['recursive_imports'] = True
            oper_args_set['imports']['read_test'] = True

        elif known_args.usual_import and not known_args.recursive_import:
            oper_args_set['imports']['usual_imports'] = True

        elif known_args.recursive_import and not known_args.usual_import:
            oper_args_set['imports']['recursive_imports'] = True

        elif known_args.usual_import and known_args.recursive_import:
            log.warning("You cannot add two import scenarios in one run. Please choose only one. "
                        "But I will run usual_imports by default.")
            oper_args_set['imports']['usual_imports'] = True

        elif known_args.related_tests and not known_args.run_test:
            log.info("Related test run option. I will search for all related "
                     "tests which use current active pattern and run them.")
            oper_args_set['tests']['related_tests'] = True

        elif known_args.run_test and not known_args.related_tests:
            log.info("Single test run options. I will run only test for current pattern in its tests folder.")
            oper_args_set['tests']['run_test'] = True

        else:
            # When situation is not implemented - use false by default.
            log.info("Operation mode is simple, no imports, no tests.")

        if known_args.wipe_tku:
            oper_args_set['tku_oper']['wipe_tku'] = True

        if known_args.test_verbose:
            oper_args_set['tests']['test_verbose'] = True

        if known_args.test_failfast:
            oper_args_set['tests']['test_failfast'] = True

        return oper_args_set
