"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import sys
import argparse
from check_ide.global_logic import GlobalLogic
from check_ide.logger import log_define

# # DEBUG
# import json
# from pprint import pformat


def parse_args_f():
    """
    Args parser function.
    Input nothing, wile exec - return tuples with known args and extra args.

    Namespace(addm_host='',
              disco_mode='',
              full_path='d:\\BMCRemedyARSystem.tplpre',
              log_lvl='debug',
              password='',
              read_test=False,
              recursive_import=False,
              related_tests=False,
              run_test=False,
              scan_host_list='',
              system_password='',
              system_user='',
              test_failfast=False,
              test_verbose=False,
              user='',
              usual_import=False,
              version_tpl='',
              wipe_tku=False)
               ['-my_extra_arg']

    :return: tuple
    """

    parser = argparse.ArgumentParser(add_help=True)
    common = parser.add_argument_group("Common options")
    developer = parser.add_argument_group("Developer options")

    wipe_tku_h         = '''Totally wipe knowledge update with tw_pattern_management --remove-all --force.'''
    usual_import_h     = '''Option imports patterns which only imported in currently opened pattern from -full_path. 
                            No recursive imports will run. If file is not a (tplpre|tpl) - this option will be ignored.'''
    recursive_import_h = '''Options imports all patterns in recursive mode including each 'imports' 
                            from each found pattern.If file is not a (tplpre|tpl) - this option will be ignored. '''
    read_test_h        = '''Read test.py file and get all patterns which used for test and import in recursive mode. 
                            Also retrieve queries and use to generate model files. '''
    run_test_h         = '''Run test which is related to current patten if test.py exist. 
                            Save result in log and in current working directory. '''
    related_tests_h    = '''Read each test.py file in tku_patterns and compose set of pattern:tests 
                            where active pattern is used. Execute each test starting from main pattern's 
                            test one by one and save result log in current pattern folder. '''
    test_verbose_h     = '''Using --verbose can also be useful to see progress in a little more detail '''
    test_failfast_h    = '''Using --failfast can be useful as the tests will stop at the first failure. '''
    tpl_h              = '''Ignored option. In progress...Set this to correspond tpl version to upload folder of 
                            TPLPreprocessor output result ignoring ADDM tpl version check_ide procedure. 
                            Use when you want upload older or newer tpl on ADDM If file is not a .tplpre
                            - this option will be ignored. '''
    # tkn_h              = ''' TKN_CORE env for TPLpreprocerssor only'''
    full_path_h        = '''Path to current edited or processed file. '''
    u_h                = '''Your ADDM user - root or tideway '''
    p_h                = '''Password for ADDM user '''
    system_user_h      = '''Your ADDM user - root or tideway '''
    system_pass_h      = '''Password for ADDM user '''
    addm_h             = '''ADDM ip address. '''
    host_list_h        = '''Host list to Discovery scan on ADDM sep by comma. '''
    disco_mode_h       = '''Choose the discovery mode: standard|playback|record '''
    l_h                = '''Please set log level -> info, quiet, warning, debug, output, err '''

    # DEV ARGS - work only for fully configured DEV environment.
    developer.add_argument("-wipe_tku", action="store_true", help=wipe_tku_h)
    developer.add_argument("-usual_import", action="store_true", help=usual_import_h)
    developer.add_argument("-recursive_import", action="store_true", help=recursive_import_h)
    developer.add_argument("-read_test", action="store_true", help=read_test_h)
    developer.add_argument("-run_test", action="store_true", help=run_test_h)
    developer.add_argument("-related_tests", action="store_true", help=related_tests_h)
    developer.add_argument("-test_verbose", action="store_true", help=test_verbose_h)
    developer.add_argument("-test_failfast", action="store_true", help=test_failfast_h)
    developer.add_argument("-tpl", type=str, action='store', dest="version_tpl", default="", help=tpl_h)
    # developer.add_argument("-tkn_core", type=str, action='store', dest="tkn_core", default="", help=tkn_h)

    # COMMON ARGS - works in most usual cases.
    common.add_argument("-full_path", type=str, action='store', dest="full_path", default="", help=full_path_h)
    common.add_argument("-u", type=str, action='store', dest="user", default="", help=u_h)
    common.add_argument("-p", type=str, action='store', dest="password", default="", help=p_h)
    common.add_argument("-system_user", type=str, action='store', dest="system_user", default="", help=system_user_h)
    common.add_argument("-system_password", type=str, action='store', dest="system_password", default="",
                        help=system_pass_h)
    common.add_argument("-addm", type=str, action='store', dest="addm_host", default="", help=addm_h)
    common.add_argument("-host_list", type=str, action='store', dest="scan_host_list", default="", help=host_list_h)
    common.add_argument("-disco_mode", type=str, action='store', dest="disco_mode", default="", help=disco_mode_h)
    common.add_argument("-l", type=str, action='store', dest="log_lvl", default="1", help=l_h)
    common.add_argument('--version', action='version', version='%(prog)s 1.1.4')

    return parser


if __name__ == "__main__":
    """
        Start execution.
        Later function execution from below will use some logic to break the execution if something fails.
        Now this just execute each "<operation_name>_f" if this is callable obj.
    """
    parser = parse_args_f()
    known_args, extra_args = parser.parse_known_args(sys.argv[1:])

    log = log_define(known_args)
    log.debug("Start: "+__name__)

    funcs_run = GlobalLogic(known_args=known_args, extra_args=extra_args)
    conditional_functions, conditional_results = funcs_run.make_function_set()

    # Manual functions execution:
    assert isinstance(conditional_functions, dict)

    if conditional_functions['imports_f']:
        imports_f = conditional_functions['imports_f']

        # Executing test queries parser:
        if callable(imports_f['parse_tests_queries']):
            parse_tests_queries = imports_f['parse_tests_queries']
            if parse_tests_queries:
                log.debug("IMPORTS:\t\tparse_tests_queries")
                parse_tests_queries()

        # Executing test patterns list get:
        if callable(imports_f['parse_tests_patterns']):
            parse_tests_patterns = imports_f['parse_tests_patterns']
            if parse_tests_patterns:
                log.debug("IMPORTS:\t\tparse_tests_patterns")
                parse_tests_patterns()

        # Executing all imports:
        if callable(imports_f['import_patterns']):
            import_patterns = imports_f['import_patterns']
            if import_patterns:
                log.debug("IMPORTS:\t\timport_patterns")
                import_patterns()

    # # Executing preprocessor:
    if callable(conditional_functions['preproc_f']):
        preproc_f = conditional_functions['preproc_f']
        if preproc_f:
            log.debug("PREPROC:\t\tpreproc_f")
            preproc_f()

    # Executing syntax checker:
    if callable(conditional_functions['syntax_check_f']):
        print("LOCAL TPL Syntax check now skipped by default!")
        pass
        # syntax_check_f = conditional_functions['syntax_check_f']
        # if syntax_check_f:
        #     log.debug("SYNTAX:\t\tsyntax_check_f")
        #     syntax_check_f()

    # Executing zipping files (and upload maybe?)
    if callable(conditional_functions['zip_files_f']):
        zip_files_f = conditional_functions['zip_files_f']
        if zip_files_f:
            log.debug("ZIP:\t\tzip_files_f")
            zip_files_f()

    # Wiping TKU!:
    if callable(conditional_functions['wipe_tku_f']):
        wipe_tku_f = conditional_functions['wipe_tku_f']
        if wipe_tku_f:
            log.debug("UPLOAD:\t\twipe_tku_f")
            wipe_tku_f()

    # Executing pattern upload:
    if callable(conditional_functions['upload_f']):
        upload_f = conditional_functions['upload_f']
        if upload_f:
            log.debug("UPLOAD:\t\tupload_f")
            upload_f()

    # Executing pattern activation:
    if callable(conditional_functions['addm_activate_f']):
        addm_activate_f = conditional_functions['addm_activate_f']
        if addm_activate_f:
            log.debug("ACTIVATE:\t\taddm_activate_f")
            addm_activate_f()

    # Executing start scan
    # # Working in current condition. Disable to save time
    if callable(conditional_functions['scan_f']):
        scan_f = conditional_functions['scan_f']
        if scan_f:
            log.debug("SCAN:\t\tscan_f")
            scan_f()

    if callable(conditional_functions['test_executor_f']):
        test_executor = conditional_functions['test_executor_f']
        if test_executor:
            log.debug("TEST EXEC:\t\ttest_executor_f")
            test_executor()

    log.info("-=== END of Check script. ===-")

