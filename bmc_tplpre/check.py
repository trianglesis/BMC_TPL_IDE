"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import argparse
from check.global_logic import GlobalLogic

# # DEBUG
# import json
# from pprint import pformat

parser = argparse.ArgumentParser(add_help=True)
common = parser.add_argument_group("Common options")
developer = parser.add_argument_group("Developer options")


developer.add_argument("-usual_import",
                       action="store_true",
                       help="Option imports patterns which only imported in currently opened pattern "
                            "from -full_path. "
                            "No recursive imports will run. "
                            "If file is not a (tplpre|tpl) - this option will be ignored.")
developer.add_argument("-recursive_import",
                       action="store_true",
                       help="Options imports all patterns in recursive mode including each 'imports' from "
                            "each found pattern."
                            "If file is not a (tplpre|tpl) - this option will be ignored.")
developer.add_argument("-read_test",
                       action="store_true",
                       help="Read test.py file and get all patterns which used for test and import in recursive mode."
                            "Also retrieve queries and use to generate model files."
                            "In progress...")
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
common.add_argument("-system_user",
                    type=str,
                    action='store',
                    dest="system_user",
                    default="",
                    help="Your ADDM user - root or tideway")
common.add_argument("-system_password",
                    type=str,
                    action='store',
                    dest="system_password",
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
# print("Known args: "+str(known_args))

def log_constructor():
    from check.logger import Logger
    log_init = Logger(known_args.log_lvl)
    return log_init.log_define()
log = log_constructor()

funcs_run = GlobalLogic(logging=log, known_args=known_args, extra_args=extra_args)
conditional_functions, conditional_results = funcs_run.make_function_set()

# Manual functions execution:
if conditional_functions['imports_f']:
    imports_f = conditional_functions['imports_f']

    # Executing test queries parser:
    if imports_f['parse_tests_queries']:
        parse_tests_queries = imports_f['parse_tests_queries']
        if parse_tests_queries:
            parse_tests_queries()

    # Executing test patterns list get:
    if imports_f['parse_tests_patterns']:
        parse_tests_patterns = imports_f['parse_tests_patterns']
        if parse_tests_patterns:
            parse_tests_patterns()

    # Executing all imports:
    if imports_f['import_patterns']:
        import_patterns = imports_f['import_patterns']
        if import_patterns:
            import_patterns()

# Executing preprocessor:
if conditional_functions['preproc_f']:
    preproc_f = conditional_functions['preproc_f']
    if preproc_f:
        preproc_f()

# Executing syntax checker:
if conditional_functions['syntax_check_f']:
    syntax_check_f = conditional_functions['syntax_check_f']
    if syntax_check_f:
        syntax_check_f()

# Executing zipping files (and upload maybe?)
if conditional_functions['zip_files_f']:
    zip_files_f = conditional_functions['zip_files_f']
    if zip_files_f:
        zip_files_f()

# Executing pattern activation:
if conditional_functions['addm_activate_f']:
    addm_activate_f = conditional_functions['addm_activate_f']
    if addm_activate_f:
        addm_activate_f()

# Executing start scan
# Working in current condition. Disable to save time
if conditional_functions['scan_f']:
    scan_f = conditional_functions['scan_f']
    if scan_f:
        scan_f()


log.info("-=== FINISHING Check script.")

