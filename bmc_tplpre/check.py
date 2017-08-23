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
                       help="Ignored option. In progress..."
                            "Set this to correspond tpl version to upload folder of TPLPreprocessor output result "
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
common.add_argument('--version',
                    action='version',
                    version='%(prog)s 1.0')

known_args, extra_args = parser.parse_known_args()
print("Known args: "+str(known_args))


def log_constructor():
    from check.logger import Logger
    log_init = Logger(known_args.log_lvl)
    return log_init.log_define()
log = log_constructor()

log.info("-=== INITIALISING Check script from here:")
log.warn("WARN TEST")
log.critical("CRITICAL TEST")

funcs_run = GlobalLogic(logging=log, known_args=known_args, extra_args=extra_args)
conditional_functions, conditional_results = funcs_run.make_function_set()
print("\tconditional_functions: "+str(conditional_functions))
print("\tconditional_results: "+str(conditional_results))

# Manual functions execution:

log.info("-=== FINISHING Check script.")