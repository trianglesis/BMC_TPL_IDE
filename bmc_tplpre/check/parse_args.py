import re
import paramiko

from check.logger import i_log
log = i_log(level='DEBUG', name=__name__)


def i_log_check(log_lvl):
    """
    Set the proper log level based on arguments.
    Used for python standard logging module.
    Check for typos and handle them.


    :param log_lvl: Input from args  # info, quiet, warn, debug, output, error
    :return: proper level for use in logger
    """

    if log_lvl:
        if "info" in log_lvl:
            log_lvl = "INFO"
        elif "warn" in log_lvl:
            log_lvl = "WARN"
        elif "error" in log_lvl:
            log_lvl = "ERROR"
        elif "critical" in log_lvl:
            log_lvl = "CRITICAL"
        elif "debug" in log_lvl:
            log_lvl = "DEBUG"
        else:
            log_lvl = "INFO"
    else:
        log_lvl = "DEBUG"

    return log_lvl


def check_working_dir(working_dir):
    """
    Function will check if --workingDirectory argument is present.
    If path have windows format - will use a first approach, if unix (like Sublime do) - will use second approach.
    If format incorrect - will warn.
    Also function tries to get parent directory name which further will be used for scan name
    if arg -full_path was not set.

    :param working_dir: path to folder where edited pattern lies.

    :return working_dir, dir_label
    """
    file_path_check = re.compile("\w:\\\\")  # File paths
    file_path_check2 = re.compile("/w:/")  # File paths

    dir_label = ''
    if working_dir:
        check = file_path_check.match(working_dir)
        if check:
            working_dir = working_dir
            dir_label = re.findall('(\w+)$', working_dir)
            dir_label = dir_label[0]
            log.debug('Working directory is: ' + working_dir)

        elif not check:
            check2 = file_path_check2.match(working_dir)
            if check2:
                working_dir = working_dir
                dir_label = re.findall('(\w+)$', working_dir)
                dir_label = dir_label[0]
                log.info('Working directory is: ' + working_dir)

            else:
                log.error('-wd argument could have wrong format!')
        else:
            log.error('-wd argument could have wrong format!')
    else:
        log.error('-wd argument could have wrong format!')

    return working_dir, dir_label


def tpl_version_check(tpl_ver):
    """
        if argument "-tpl", "--TPL_Version" is set - will try to check it's format and version. Then will compose
        path to folder where TPLPreprocessor should output for current version:
        - at first will run syntax check with this version (tplint)
        - will try to check if folder for this version was created after Tplpreproc

        If no argument set - will WARN and pass this and return None

        (Discovery/TPL versions: 8.3(1.6) 9.0(1.7) 10.0(1.8) 10.1(1.9) 10.2(1.10) 11.0(1.11))
        :param tpl_ver: str

        :return: tpl_folder, tpl_version
        """

    tpl_ver_check = re.compile("\d+\.\d+")  # TPl ver 10.2,11.0...
    tpl_folder_k = {'8.3': 'tpl16',
                    '9.0': 'tpl17',
                    '10.0': 'tpl18',
                    '10.1': 'tpl19',
                    '10.2': 'tpl110',
                    '11.2': 'tpl112',
                    '11.3': 'tpl113',
                    '11.4': 'tpl114'
                    }

    tpl_version = ''
    tpl_folder = ''

    if tpl_ver:
        check = tpl_ver_check.match(tpl_ver)
        if check:
            tpl_version = tpl_ver
            if tpl_ver in tpl_folder_k:
                tpl_folder = tpl_folder_k[tpl_ver]
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


def full_current_path_check(full_curr_path, working_dir, tpl_folder):
    """
    Check arg "-full_path", "--FULL_CURRENT_PATH"
    This is full path to currently edited pattern.
    If argument is present - will start process with this one file, if not - will pass (and run on working dir)

    Also check if tpl version passed into argument "-tpl", "--TPL_Version" from function tpl_version_check()
    Additionally tries to get pattern's file name - to use it in fali path and further in scan name
        -if tpl arg is present - will compose file path with Tplpreproc output folder in it
        example: D:\Doc\PerForce\addm\tkn_main\tku_patterns\CORE\SupportingFiles\tpl113\
        if no tpl arg - will compose file path just to currently open file:
        example: D:\Doc\PerForce\addm\tkn_main\tku_patterns\CORE\SupportingFiles\tpl113\J2EEInferredModel.tpl


    :param full_curr_path:
    :param working_dir:
    :param tpl_folder:
    :return:
    """
    full_curr_path_check = re.compile('\w:\S+\.(?:tplpre|tpl)')
    pattern_path = ''  # path to developed pattern file
    pattern_name = ''  # extracted pattern name from full_path_dev
    # file_path = ''  # path to ready tpl file - will be composed.
    pattern_file_path = ''  # path to tplver folder for current pattern

    if full_curr_path:
        log.debug("Full path arg: " + full_curr_path)
        file_path = working_dir+'\\'+tpl_folder+'\\'
        check = full_curr_path_check.match(full_curr_path)
        if check:
            pattern_path = full_curr_path
            pattern_name_ext = re.findall("(\w+)\.(?:tplpre|tpl)", full_curr_path)
            if pattern_name_ext:
                pattern_name = pattern_name_ext[0]
                if tpl_folder:
                    pattern_file_path = working_dir + '\\' + tpl_folder + '\\' + pattern_name + ".tpl"
                    log.debug("Path to single file which can be uploaded to ADDM: " + str(file_path))
                else:
                    pattern_file_path = working_dir + '\\' + pattern_name + ".tpl"
                    log.debug("Path to single file which can be uploaded to ADDM: " + " " * 7 + str(file_path))
        else:
            if full_curr_path:
                log.error("'-full_path' should have format"+" "*3+"'\w:\S+\.tplpre'")
    else:
        file_path = working_dir+'\\'+tpl_folder+'\\'
        if full_curr_path:
            log.error("'-full_path' should have format"+" "*3+"'\w:\S+\.tplpre'")

    return file_path, pattern_name, pattern_path, pattern_file_path


def addm_host_check(addm_host, user, password):
    """
    Check login and password for provided ADDM IP
    If no ADDM IP - should not run this and upload, disco.
    Check ADDM host IP where to upload and scan
    Should checked at first - before upload, scan, disco

    :param password: str
    :param user: str
    :param addm_host: str
    """
    # user = ''
    ip_addr_check = re.compile("\d+\.\d+\.\d+\.\d+")  # ip addr

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
        check = ip_addr_check.match(addm_host)
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


def discovery_mode_check(disco_mode):
    """
    Check the discovery mode to run discovery
     (standard|playback|record)
     Should run only if SSH session established!
    """
    # disco_mode = '' # check discovery mode
    disco_mode_check = re.compile("standard|playback|record")  # standard|playback|record

    if disco_mode:
        check = disco_mode_check.match(disco_mode)
        if check:
            disco_mode = disco_mode  # Discovery mode is:         standard
            log.info("INFO: Discovery mode is: " + " " * 39 + str(disco_mode))
    else:
        log.info("INFO: Discovery mode not set or not used.")

    return disco_mode


def host_list_check(host_list):
    """
    Check host list before start scan
    Will add hostname support maybe
    Should run only if SSH session established!
    :param host_list:
    """
    # HOSTs ip check:NoneNone
    # host_list = ''
    ip_addr_check = re.compile("\d+\.\d+\.\d+\.\d+")  # ip addr

    if host_list:
        check = ip_addr_check.match(host_list)
        if check:
            host_list = host_list  # Host(s) to scan are:       10.49.32.114
            log.debug("DEBUG: Will add host(s) for discvovery with IP: " + " " * 18 + str(host_list))
    else:
        host_list = False
        if host_list != 'None':
            log.error("Please specify some hosts to scan for ADDM!")
        else:
            log.info("INFO: Pattern upload only. No host added for Discovery run!")

    return host_list
