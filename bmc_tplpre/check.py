

import argparse
from check.parse_args import *
from check.upload import *
from check.syntax_checker import syntax_check, parse_syntax_result
from check.preproc import tpl_preprocessor
from check.scan import addm_scan

# from check.imports import *
# from check.internal import *


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-wd", "--workingDirectory",
                    type=str,
                    dest="working_dir",
                    default="",
                    help="Working dir where tpl files are")
parser.add_argument("-tpl", "--TPL_Version",
                    type=str,
                    action='store',
                    dest="version_tpl",
                    default="",
                    help="TPL version to check with: 10.2,11.0")
parser.add_argument("-full_path", "--FULL_CURRENT_PATH",
                    type=str,
                    action='store',
                    dest="full_curr_path",
                    default="",
                    help="var from Notepad $(FULL_CURRENT_PATH)")
parser.add_argument("-addm", "--addmHost",
                    type=str,
                    action='store',
                    dest="addm_host",
                    default="",
                    help="Test addm machine IP address")
parser.add_argument("-host_list", "--ScanHostList",
                    type=str,
                    action='store',
                    dest="scan_host_list",
                    default="",
                    help="Host list to scan with ADDM sep by comma.")
parser.add_argument("-disco_mode", "--DiscoveryMode",
                    type=str,
                    action='store',
                    dest="disco_mode",
                    default="",
                    help="Choose the discovery mode: standard|playback|record")
parser.add_argument("-u", "--user",
                    type=str,
                    action='store',
                    dest="user",
                    default="",
                    help="Your ADDM user - root or tideway")
parser.add_argument("-p", "--password",
                    type=str,
                    action='store',
                    dest="password",
                    default="",
                    help="Password for ADDM user")
parser.add_argument("-l", "--logLevel",
                    type=str,
                    action='store',
                    dest="log_lvl",
                    default="1",
                    help="Please set log level")  # info, quiet, warn, debug, output, error

known_args, extra_args = parser.parse_known_args()
args = known_args

log, message = log_check(args.log_lvl)
message_print(message, log)

# Path to this script and tplint binaries
sublime_working_dir = os.path.dirname(os.path.abspath(__file__))
# sublime_working_dir = "C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre"

# Checking of working dir set correctly (It's a folder where patter lies):
working_dir, dir_label, message = check_working_dir(args.working_dir)
message_print(message, log)

if working_dir:

    '''
    This will try to read current pattern or each pattern in working directory, find import modules
    and then try to find them in SupportingFiles and copy to a working directory.
    No need to use it now.
    '''

    # import_included_modules, message = import_modules(working_dir)
    # message_print(message, log)

    ''' Check if tpl version arguments set. Required for syntax check and upload after tplpreproc '''
    tpl_folder, version_tpl, message = tpl_version_check(args.version_tpl)
    message_print(message, log)

    ''' Check if full path to currently working patten set or will run on the whole folder with bunch of patterns '''
    result_file_path, pattern_name, pattern_path, pattern_file_path, message = full_current_path_check(args.full_curr_path,
                                                                                    working_dir=working_dir,
                                                                                    tpl_folder=tpl_folder)
    message_print(message, log)
    # print("pattern_file_path PATH: "+str(pattern_file_path))
    # print("result_file_path PATH: "+str(result_file_path))

    ''' Local fast syntax and types check. Under development for custom linting. '''
    # if extra_args:
    #     local_syntax_check(extra_args[0])

    '''
    If  tpl folder composed - will run TplPreprocessor on one of two options:
    1. on pattern in %file_path% 2. on whole folder in %working_dir%
    Then Syntax check will run on preproc result folder with tpl version which was set in args
    '''
    preproc_result = False
    if tpl_folder and result_file_path:
        preproc_result, message = tpl_preprocessor(sublime_working_dir=sublime_working_dir,
                                                   working_dir=working_dir,
                                                   dir_label=dir_label,
                                                   full_curr_path=pattern_path,
                                                   file_path=result_file_path)
        message_print(message, log)

    syntax_passed = False
    if preproc_result:
        syntax_passed, message, result = syntax_check(curr_work_dir=sublime_working_dir,
                                                      working_dir=result_file_path,
                                                      tpl_version=version_tpl)
        message_print(message, log)

        # Make output as STDERR for linter plugin with "-l quiet"
        if log == 4:
            parse_syntax_result(result)

    '''
    1. Scenario:
    When syntax check is OK and args have addm IP, user and password.
    This will try to open SSH session and check if it's alive.
    Then it will check if ADDM has needed folders and wipe old files on them.
    Then if will try to upload file or files (as zip) from local path
    It will use folder after TPLpreprocessor and if there is -full_path arg - upload this one file,
    if no -full_path arg - folder content will be zipped and sent.
    Based on full_current_path_check() :result_file_path

    2. Scenario
    In case - when user wants to upload clean tpl file or folder which was created before (or manually)
    this tool will run the second scenario. When args have addm credentials and IP but have no tpl-ver and
    Tplpreprocessor was not run - this scenario will upload currently opened file or folder.

    '''
    ssh = ''
    uploaded_activated = False
    if syntax_passed and (args.addm_host and args.user and args.password):
        ssh, message = addm_host_check(addm_host=args.addm_host,
                                       user=args.user,
                                       password=args.password)
        message_print(message, log)

        if ssh.get_transport().is_active():
            if log == (1 or 2 or 3 or 0):
                print("SSH connection os ON!")

            folders, message = check_folders(path="/usr/tideway/TKU/Tpl_DEV", ssh=ssh)
            message_print(message, log)

            if pattern_file_path:
                output, uploaded_activated, message = upload_knowledge(ssh, pattern_name, dir_label, pattern_file_path)
                message_print(message, log)
            else:
                output, uploaded_activated, message = upload_knowledge(ssh, pattern_name, dir_label, result_file_path)
                message_print(message, log)

    elif args.addm_host and args.user and args.password and not preproc_result:
        ssh, message = addm_host_check(addm_host=args.addm_host,
                                       user=args.user,
                                       password=args.password)
        message_print(message, log)

        if ssh.get_transport().is_active():
            if log == (1 or 2 or 3 or 0):
                print("SSH connection os ON!")

            folders, message = check_folders(path="/usr/tideway/TKU/Tpl_DEV", ssh=ssh)
            message_print(message, log)

            output, uploaded_activated, message = upload_knowledge(ssh, pattern_name, dir_label, result_file_path)
            message_print(message, log)

    '''
    This section will start if upload_knowledge() returnt True in :uploaded_activated
    This means that uploaded patterns was activated without errors or warnings.
    Then it will check current discovery mode and switch it to one from args (if exist), if -disco_mode arg
    is not present will use 'standard'
    If arg -hosl_list is present and -disco_mode is set - will start scan with hosts from -host_list arg.
    '''
    if uploaded_activated:

        disco_mode, message = discovery_mode_check(disco_mode=args.disco_mode)
        message_print(message, log)

        host_list, message = host_list_check(host_list=args.scan_host_list)
        message_print(message, log)

        if host_list and disco_mode:
            start_scan = addm_scan(ssh, disco_mode, host_list, dir_label)
            message_print(start_scan, log)
            ssh.close()
