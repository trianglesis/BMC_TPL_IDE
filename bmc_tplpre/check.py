"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import argparse
import os

from check.global_logic import GlobalLogic


parser = argparse.ArgumentParser(add_help=True)
common = parser.add_argument_group("Common options")
developer = parser.add_argument_group("Developer options")

developer.add_argument("-tpl",
                       type=str,
                       action='store',
                       dest="version_tpl",
                       default="",
                       help="Set this to correspond tpl version to upload folder of TPLPreprocessor output result "
                            "ignoring ADDM tpl version check procedure. "
                            "Use when you want upload older or newer tpl on ADDM"
                            "If file is not a .tplpre - this option will be ignored.")
developer.add_argument("-imp",
                       action="store_true",
                       help="Set if you want to import patterns only imported in current opened pattern "
                            "from -full_path. "
                            "No recursive imports will run. "
                            "If file is not a .tplpre - this option will be ignored.")
developer.add_argument("-r_imp",
                       action="store_true",
                       help="Set if you want to import all patterns in recursive mode and upload this package on ADDM."
                            "Better use on clear TKN."
                            "If file is not a .tplpre - this option will be ignored.")
developer.add_argument("-T",
                       action="store_true",
                       help="Run validation process after scan is finished."
                            "This will use set of queries to grab everything from scan and build SI models."
                            "si_type will be gathered from pattern blocks and used to compose search query."
                            "model file will be saved into developers folder: /usr/tideway/TKU/models")
common.add_argument("-full_path",
                    type=str,
                    action='store',
                    dest="full_path",
                    default="",
                    help="Path to current edited or processed file.")
common.add_argument("-u",
                    type=str,
                    action='store',
                    dest="user",
                    default="",
                    help="Your ADDM user - root or tideway")
common.add_argument("-p",
                    type=str,
                    action='store',
                    dest="password",
                    default="",
                    help="Password for ADDM user")
common.add_argument("-addm",
                    type=str,
                    action='store',
                    dest="addm_host",
                    default="",
                    help="ADDM ip address.")
common.add_argument("-host_list",
                    type=str,
                    action='store',
                    dest="scan_host_list",
                    default="",
                    help="Host list to Discovery scan on ADDM sep by comma.")
common.add_argument("-disco_mode",
                    type=str,
                    action='store',
                    dest="disco_mode",
                    default="",
                    help="Choose the discovery mode: standard|playback|record")
common.add_argument("-l",
                    type=str,
                    action='store',
                    dest="log_lvl",
                    default="1",
                    help="Please set log level")  # info, quiet, warn, debug, output, error
common.add_argument('--version', action='version', version='%(prog)s 1.0')

known_args, extra_args = parser.parse_known_args()
print(known_args)


def log_constructor():
    from check.logger import Logger
    log_init = Logger(known_args.log_lvl)
    return log_init.log_define()
log = log_constructor()

log.info("-=== INITIALISING Check script from here:")
log.warn("WARN TEST")
log.critical("CRITICAL TEST")


funcs_run = GlobalLogic(log, known_args, extra_args)
functions_set = funcs_run.make_function_set()
print("FUNCTIONS OBJ SET: "+str(functions_set))

# Manual functions execution:
# TODO: This will be removed and execute only by set of composed functions.

import_patterns = functions_set['import_patterns']
# import_patterns()

test_patterns = functions_set['parse_tests_patterns']
# print(test_patterns)
make_preproc = functions_set['prepcoc_patterns']
# make_preproc()


# True\False check TEST


# parse_args = ArgsParse(log)
# parsable_args_set = parse_args.gather_args(known_args, extra_args)
# full_path_args = parsable_args_set

# Path to this script and tplint binaries
# sublime_working_dir = os.path.dirname(os.path.abspath(__file__))
# sublime_working_dir = "C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre"
# log.debug("Using script path as: " + sublime_working_dir)

# Not sure if we need this, or maybe just subproc this and nevermind
# tpl_preproc = Preproc(log)
# tpl_preproc_dir, tpl_preproc_py = tpl_preproc.find_tplpreprocessor(workspace=full_path_args['workspace'])
# tpl_preprocessor_class, tpl_preprocessor_main, supported_addm_ver, supported_tpl_ver = tpl_preproc.read_tplpreprocessor(tpl_preproc_dir)

# Preproc in usual way


# ADDM ARGS CHECK




# if full_path_args['file_ext'] == "tplpre":
#
#     '''
#     This will try to read current pattern or each pattern in working directory, find import modules
#     and then try to find them in SupportingFiles and copy to a working directory.
#     No need to use it now.
#     '''
#
#     # To be removed from here to GlobalLogic
#     # import_included_modules = import_modules(working_dir)
#
#     '''
#     To be REMOVEd - will use path functions or preproc for tplver get and compare with ADDM tpl ver.
#     Check if tpl version arguments set. Required for syntax check and upload after tplpreproc
#
#     tpl_folder, version_tpl = tpl_version_check(args.version_tpl)
#     '''
#
#
#     '''
#     DECOMMISSION: will use full_path_args()
#     result_file_path, pattern_name, pattern_path, pattern_file_path = full_current_path_check(args.full_curr_path,
#                                                                                     working_dir=working_dir,
#                                                                                     tpl_folder=tpl_folder)
#     '''
#
#     # print("pattern_file_path PATH: "+str(pattern_file_path))
#     # print("result_file_path PATH: "+str(result_file_path))
#
#     ''' Local fast syntax and types check. Under development for custom linting. '''
#     # if extra_args:
#     #     local_syntax_check(extra_args[0])
#
#     '''
#     If  tpl folder composed - will run TplPreprocessor on one of two options:
#     1. on pattern in %file_path% 2. on whole folder in %working_dir%
#     Then Syntax check will run on preproc result folder with tpl version which was set in args
#     '''
#     preproc_result = False
#     # TODO: Remove:
#     tpl_folder = False
#     if tpl_folder and result_file_path:
#
#         # preproc_result = tpl_preprocessor(tpl_preproc_py, tpl_preprocessor_class, full_path_args_dict)
#         # preproc_result = tpl_preprocessor(tpl_preproc_dir, tpl_preprocessor_main, full_path_args_dict)
#
#         preproc_result = tpl_preprocessor_old(sublime_working_dir=tpl_preproc_dir,
#                                           working_dir=working_dir,
#                                           dir_label=dir_label,
#                                           full_curr_path=pattern_path,
#                                           file_path=result_file_path)
#
#
#
#     syntax_passed = False
#     if preproc_result:
#         syntax_passed, result = syntax_check(curr_work_dir=sublime_working_dir,
#                                              working_dir=result_file_path,
#                                              tpl_version=version_tpl)
#
#         # Make output as STDERR for linter plugin with "-l quiet"
#         if log == 4:
#             parse_syntax_result(result)
#
#     '''
#     1. Scenario:
#     When syntax check is OK and args have addm IP, user and password.
#     This will try to open SSH session and check if it's alive.
#     Then it will check if ADDM has needed folders and wipe old files on them.
#     Then if will try to upload file or files (as zip) from local path
#     It will use folder after TPLpreprocessor and if there is -full_path arg - upload this one file,
#     if no -full_path arg - folder content will be zipped and sent.
#     Based on full_current_path_check() :result_file_path
#
#     2. Scenario
#     In case - when user wants to upload clean tpl file or folder which was created before (or manually)
#     this tool will run the second scenario. When args have addm credentials and IP but have no tpl-ver and
#     Tplpreprocessor was not run - this scenario will upload currently opened file or folder.
#
#     '''
#     ssh = ''
#     uploaded_activated = False
#     if syntax_passed and (args.addm_host and args.user and args.password):
#         ssh = addm_host_check(addm_host=args.addm_host,
#                               user=args.user,
#                               password=args.password)
#
#         if ssh.get_transport().is_active():
#             if log == (1 or 2 or 3 or 0):
#                 print("SSH connection os ON!")
#
#             folders = check_folders(path="/usr/tideway/TKU/Tpl_DEV", ssh=ssh)
#
#             if pattern_file_path:
#                 output, uploaded_activated = upload_knowledge(ssh, pattern_name, dir_label, pattern_file_path)
#             else:
#                 output, uploaded_activated = upload_knowledge(ssh, pattern_name, dir_label, result_file_path)
#
#     elif args.addm_host and args.user and args.password and not preproc_result:
#         ssh = addm_host_check(addm_host=args.addm_host,
#                               user=args.user,
#                               password=args.password)
#
#         if ssh.get_transport().is_active():
#             if log == (1 or 2 or 3 or 0):
#                 print("SSH connection os ON!")
#
#             folders = check_folders(path="/usr/tideway/TKU/Tpl_DEV", ssh=ssh)
#
#             output, uploaded_activated = upload_knowledge(ssh, pattern_name, dir_label, result_file_path)
#
#     '''
#     This section will start if upload_knowledge() returnt True in :uploaded_activated
#     This means that uploaded patterns was activated without errors or warnings.
#     Then it will check current discovery mode and switch it to one from args (if exist), if -disco_mode arg
#     is not present will use 'standard'
#     If arg -hosl_list is present and -disco_mode is set - will start scan with hosts from -host_list arg.
#     '''
#     if uploaded_activated:
#
#         disco_mode = discovery_mode_check(disco_mode=args.disco_mode)
#
#         host_list = host_list_check(host_list=args.scan_host_list)
#
#         if host_list and disco_mode:
#             start_scan = addm_scan(ssh, disco_mode, host_list, dir_label)
#             ssh.close()

log.info("-=== FINISHING Check script.")