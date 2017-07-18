import sublime
import sublime_plugin

import os, re, sys
import subprocess




# sys.path.append(os.path.join(os.path.dirname(__file__), "bmc_tplpre"))



print("CLEAR\n\n\n")

class SettingsTplpre(object):
    '''
        Manually set set of settings which should be
        competed with p4_wd from syntax spec settings file:
        FILE: tplpre_READY.sublime-settings
    '''

    ADDM_PATH         = "addm"
    TKN_MAIN          = "tkn_main"
    BUILDSCRIPTS      = "buildscripts"
    TKU_PATTERNS      = "tku_patterns"
    CORE              = "CORE"
    DBDETAILS         = "DBDETAILS"
    MIDDLEWAREDETAILS = "MIDDLEWAREDETAILS"
    SYSTEM            = "SYSTEM"
    SANDBOX           = "tkn_sandbox"


    def local_paths_settings(self, p4_wd):
        '''
            Generating all needed path with pattern-file names and etc.
            Use global vars from class
            Then add local paths
            Return dict with options.

            OUTPUT EXAMPLE:
            local_settings IS
                {'BUILDSCRIPTS': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\', 'path_to_move_expected_data': 'D:\\perforce\\addm\\tkn_sandbox\\v.ratniuk\\TH_tools\\move_expected_data.py', 'TKU_PATTERNS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\', 'MIDDLEWAREDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS', 'TKN_MAIN': 'D:\\perforce\\addm\\tkn_main\\', 'DBDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS', 'SANDBOX': 'D:\\perforce\\addm\\tkn_sandbox\\', 'core_path': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\', 'type': 'Local path settings', 'path_to_dan_sublime_modules': 'D:\\perforce\\addm\\tkn_sandbox\\o.danylchenko\\projects\\Notepad_IDE\\Sublime\\TPL_IDE\\bmc_tplpre\\', 'p4_wd': 'D:\\perforce\\', 'path_to_tplpreprocessor': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py', 'SYSTEM': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\SYSTEM'}

            # buildscripts_path      = tkn_main_path     + SettingsTplpre.BUILDSCRIPTS + SEP
        '''
        to = SettingsTplpre()
        sep = "\\"
        DANILCHA = "o.danylchenko" + sep

        DAN_SUBLIME_MODULES = "projects\\Notepad_IDE\\Sublime\\TPL_IDE\\bmc_tplpre" + sep
        VADYM               = "v.ratniuk"

        # python27            = "C:\\Python27\\python.exe"
        # python34            = "C:\\Python34\\python.exe"

        p4_wd               = p4_wd + sep
        tkn_main_path       = p4_wd + to.ADDM_PATH + sep + to.TKN_MAIN + sep
        sandbox_path        = p4_wd + to.ADDM_PATH + sep + to.SANDBOX + sep

        buildscripts_path   = tkn_main_path + to.BUILDSCRIPTS + sep
        tku_patterns_path   = tkn_main_path + to.TKU_PATTERNS + sep

        core_path              = tku_patterns_path + to.CORE + sep
        dbdetails_path         = tku_patterns_path + to.DBDETAILS
        middlewaredetails_path = tku_patterns_path + to.MIDDLEWAREDETAILS
        system_path            = tku_patterns_path + to.SYSTEM

        path_to_move_expected_data  = sandbox_path + VADYM + sep + "TH_tools\\move_expected_data.py"
        path_to_tplpreprocessor     = buildscripts_path + "TPLPreprocessor.py"
        path_to_dan_sublime_modules = sandbox_path + DANILCHA + DAN_SUBLIME_MODULES

        two = "Local path settings"

        local_paths_settings_dict = {
                                     "BUILDSCRIPTS":buildscripts_path,
                                     "core_path":core_path,
                                     "DBDETAILS":dbdetails_path,
                                     "MIDDLEWAREDETAILS":middlewaredetails_path,
                                     "type":two,
                                     "path_to_dan_sublime_modules":path_to_dan_sublime_modules,
                                     "path_to_move_expected_data":path_to_move_expected_data,
                                     "path_to_tplpreprocessor":path_to_tplpreprocessor,
                                     "p4_wd":p4_wd,
                                     "SANDBOX":sandbox_path,
                                     "SYSTEM":system_path,
                                     "TKN_MAIN":tkn_main_path,
                                     "TKU_PATTERNS":tku_patterns_path
                                     }
        return local_paths_settings_dict


    def remote_paths_settings(self, edit, addm_dev, tideway_usr):
        '''
            Generating all needed path with pattern-file names and etc.
            Use global vars from class
            Then add local paths
            Return dict with options.

            Patter name parsing from sublime built in function
                FROM class ArgumentsAdd(sublime_plugin.TextCommand):
            Then it will be parsed in one of two ways:
               1. view_file_name = ArgsInterpret.args_output(self, edit)['view_file_name']
               2. view_file_name = ArgumentsAdd.run(self, edit)['view_file_name']
            1. Is needed to be sure option will be parsed out.
            2. Is working fine now - let it be.

            OUTPUT EXAMPLE:
            remote_settings IS
                {'view_file_name': 'test', 'addm_dev': '/usr/tideway/TKU/', 'BUILDSCRIPTS': '/usr/tideway/TKU/addm/tkn_main/buildscripts/', 'pattern_dml': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/dml/', 'pattern_actuals': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/actuals/', 'TKU_PATTERNS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/', 'MIDDLEWAREDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/MIDDLEWAREDETAILS/', 'DML_COMMON_PATH': '/usr/tideway/TKU/DML/', 'pattern_test': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/', 'DBDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/DBDETAILS/', 'core_path': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/', 'TKN_MAIN': '/usr/tideway/TKU/addm/tkn_main/', 'TKU_UPLOAD_PATH': '/usr/tideway/TKU/TKU_Upload/', 'TPL_DEV_PATH': '/usr/tideway/TKU/Tpl_DEV/', 'type': 'Remote path settings', 'pattern_expected': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/expected/', 'SYSTEM': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/SYSTEM/'}
        '''
        to = SettingsTplpre()
        sep = "/"

        addm_dev               = addm_dev + sep
        tkn_main_path          = addm_dev + to.ADDM_PATH + sep + to.TKN_MAIN + sep

        buildscripts_path      = tkn_main_path     + to.BUILDSCRIPTS + sep
        tku_patterns_path      = tkn_main_path     + to.TKU_PATTERNS + sep
        dbdetails_path         = tku_patterns_path + to.DBDETAILS + sep
        core_path              = tku_patterns_path + to.CORE + sep
        middlewaredetails_path = tku_patterns_path + to.MIDDLEWAREDETAILS + sep
        system_path            = tku_patterns_path + to.SYSTEM + sep

        DML_COMMON_PATH        = addm_dev + "DML"        + sep
        TPL_DEV_PATH           = addm_dev + "Tpl_DEV"    + sep
        TKU_UPLOAD_PATH        = addm_dev + "TKU_Upload" + sep


        view_file_name = FileParse.run(self, edit)['view_file_name']


        pattern_test     = core_path    + view_file_name + sep + "tests" + sep
        pattern_dml      = pattern_test + "dml"        + sep
        pattern_actuals  = pattern_test + "actuals"    + sep
        pattern_expected = pattern_test + "expected"   + sep

        two = "Remote path settings"

        remote_paths_settings_dict = {
                                     "addm_dev":addm_dev,
                                     "BUILDSCRIPTS":buildscripts_path,
                                     "core_path":core_path,
                                     "DBDETAILS":dbdetails_path,
                                     "DML_COMMON_PATH":DML_COMMON_PATH,
                                     "MIDDLEWAREDETAILS":middlewaredetails_path,
                                     "type":two,
                                     "pattern_actuals":pattern_actuals,
                                     "pattern_dml":pattern_dml,
                                     "pattern_expected":pattern_expected,
                                     "view_file_name":view_file_name,
                                     "pattern_test":pattern_test,
                                     "SYSTEM":system_path,
                                     "TKN_MAIN":tkn_main_path,
                                     "TKU_PATTERNS":tku_patterns_path,
                                     "TKU_UPLOAD_PATH":TKU_UPLOAD_PATH,
                                     "TPL_DEV_PATH":TPL_DEV_PATH
                                     }
        return remote_paths_settings_dict


    def addm_settings(self):

        '''
        Better to store this settings in CFG file whereever and parse it for each iteration.
        '''
        TIDEWAY_USER = "tideway"
        TIDEWAY_USER_PASSWORD = "system"
        ROOT_USER = "root"
        ROOT_USER_PASSWORD = "local_R00T"

        '''
        This should be a list of ADDMs maybe from another CFG file stored somewhere in user space
        '''
        ADDM_IP = "192.168.5.9"

        '''
        ADDM paths should be stale for all users.
        '''
        two = "This is ADDM connection settings"

        addm_settings_dict = {
                             "TIDEWAY_USER":TIDEWAY_USER,
                             "TIDEWAY_USER_PASSWORD":TIDEWAY_USER_PASSWORD,
                             "ROOT_USER":ROOT_USER,
                             "ROOT_USER_PASSWORD":ROOT_USER_PASSWORD,
                             "ADDM_IP":ADDM_IP,
                             "type":two
                             }

        return addm_settings_dict


class ComposeSettings(sublime_plugin.TextCommand):
    '''
        Data types:
            INPUTS:
                # Settings from the tplpre_READY.sublime-settings
                ,
                    "bmc_tplpre_settings": {
                                            "p4_wd":"D:\\perforce",
                                            "tideway_usr":"/usr/tideway",
                                            "addm_dev":"/usr/tideway/TKU",
                                            "tpl_max_ver":"113",
                                            "tpl_min_ver":"16",
                                            "python27":"C:\\Python27\\python.exe",
                                            "python34":"C:\\Python34\\python.exe"
                                           }

            OUTPUTS:
                Window CLASS in TEXT current_settings:
                    local_settings IS
                        {'BUILDSCRIPTS': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\', 'path_to_move_expected_data': 'D:\\perforce\\addm\\tkn_sandbox\\v.ratniuk\\TH_tools\\move_expected_data.py', 'TKU_PATTERNS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\', 'MIDDLEWAREDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS', 'TKN_MAIN': 'D:\\perforce\\addm\\tkn_main\\', 'DBDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS', 'SANDBOX': 'D:\\perforce\\addm\\tkn_sandbox\\', 'core_path': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\', 'type': 'Local path settings', 'path_to_dan_sublime_modules': 'D:\\perforce\\addm\\tkn_sandbox\\o.danylchenko\\projects\\Notepad_IDE\\Sublime\\TPL_IDE\\bmc_tplpre\\', 'p4_wd': 'D:\\perforce\\', 'path_to_tplpreprocessor': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py', 'SYSTEM': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\SYSTEM'}
                    remote_settings IS
                        {'view_file_name': 'test', 'addm_dev': '/usr/tideway/TKU/', 'BUILDSCRIPTS': '/usr/tideway/TKU/addm/tkn_main/buildscripts/', 'pattern_dml': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/dml/', 'pattern_actuals': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/actuals/', 'TKU_PATTERNS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/', 'MIDDLEWAREDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/MIDDLEWAREDETAILS/', 'DML_COMMON_PATH': '/usr/tideway/TKU/DML/', 'pattern_test': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/', 'DBDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/DBDETAILS/', 'core_path': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/', 'TKN_MAIN': '/usr/tideway/TKU/addm/tkn_main/', 'TKU_UPLOAD_PATH': '/usr/tideway/TKU/TKU_Upload/', 'TPL_DEV_PATH': '/usr/tideway/TKU/Tpl_DEV/', 'type': 'Remote path settings', 'pattern_expected': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/expected/', 'SYSTEM': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/SYSTEM/'}
                    current_arguments IS
                        {'view_file_name': 'test', 'filepath': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\ApacheHBase\\tests\\test.py', 'python34': 'C:\\Python34', 'python27': 'C:\\Python27', 'working_dir': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\ApacheHBase\\tests', 'plugin_dir': 'C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre', 'view_file_dir': 'ApacheHBase', 'file_extension': 'py', 'result_folder': '\\113'}

        Docs:
            DOC:
            https://stackoverflow.com/questions/19524926/get-current-file-name-from-sublime-plugin-windowcommand
    '''
    def run(self, edit):

        # Settings from the tplpre_READY.sublime-settings
        settings_f  = self.view.settings().get('bmc_tplpre_settings')
        p4_wd       = settings_f['p4_wd']
        python27    = settings_f['python27']
        python34    = settings_f['python34']
        tpl_max_ver = settings_f['tpl_max_ver']
        tpl_min_ver = settings_f['tpl_min_ver']
        addm_dev    = settings_f['addm_dev']
        tideway_usr = settings_f['tideway_usr']

        # result_folder = "\\tpl113"
        result_folder = "\\" + tpl_max_ver
        plugin_dir = os.path.dirname(os.path.abspath(__file__))

        # FileParse
        file = FileParse.run(self, edit)
        filepath = file['filepath']
        try:
            working_dir = file['working_dir']
            view_file_dir = file['view_file_dir']
            view_file_name = file['view_file_name']
            file_extension = file['file_extension']
            current_arguments = {
                     "working_dir":working_dir,
                     "view_file_dir":view_file_dir,
                     "view_file_name":view_file_name,
                     "file_extension":file_extension,
                     "filepath":filepath,
                     "result_folder":result_folder,
                     "plugin_dir":plugin_dir,
                     "python27":python27,
                     "python34":python34
                     }
        except:
            raise InputError(filepath,"working_dir was not extracted!")


        # Settings from SettingsTplpre
        local_settings = SettingsTplpre.local_paths_settings(self, p4_wd)
        remote_settings = SettingsTplpre.remote_paths_settings(self, edit, addm_dev, tideway_usr)

        various_settings = {
                            "local_settings":local_settings,
                            "remote_settings":remote_settings,
                            "current_arguments":current_arguments
                            }

        return various_settings


class FileParse(sublime_plugin.TextCommand):
    """
    This is to add arguments for syntax or TPLPRE and etc.
        {'filepath': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\CAWilyIntroscope\\CAWilyIntroscope.tplpre',
        'view_file_name': 'CAWilyIntroscope',
        'plugin_dir': 'C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre',
        'working_dir': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\CAWilyIntroscope',
        'view_file_dir': 'CAWilyIntroscope',
        'result_folder': 'CAWilyIntroscope\\tpl113'}
    """
    def run(self, edit):

        # Regexes:
        # Check is patten or model or test.py etc.
        # Parse pattern:
        # (?P<working_dir>(?P<core>\S+)\\(?P<view_file_dir>\S+))\\(?P<view_file_name>\S+)\.(?P<file_extension>(tplpre|py|dml|model|tpl))
        path_parse = re.compile(r'(?P<working_dir>(?P<core>\S+)\\(?P<view_file_dir>\S+))\\(?P<view_file_name>\S+)\.(?P<file_extension>(tplpre|py|dml|dmltemp|model|tpl))')
        test_folder = re.compile(r'\S+\\(?P<pattern_folder>\S+)\\(tests)\\(test)\.py')
        dml_test_folder = re.compile(r'\S+\\(?P<pattern_folder>\S+)\\(tests)\\(dml)\\(?P<dml_file>\S+)\.(?P<dml_ext>dmltemp|dml[^temp])')
        expected_test_folder = re.compile(r'\S+\\(?P<pattern_folder>\S+)\\(tests)\\(expected)\\(?P<expected_file>\S+)')
        actuals_test_folder = re.compile(r'\S+\\(?P<pattern_folder>\S+)\\(tests)\\(actuals)\\(?P<actuals_file>\S+)')
        tpl_pattern_folder = re.compile(r'\S+\\(?P<pattern_folder>\S+)\\(?P<tpl_ver_folder>tpl\d+)\\(?P<pattern_name>\S+\.tpl)')


        # Parsing current open file (if TPLPRE)
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = self.view.file_name()

        arguments = {"filepath":filepath}
        working_dir_parse = path_parse.match(filepath)
        if working_dir_parse:
            file_extension = working_dir_parse.group('file_extension')
            if "tplpre" in file_extension:
                working_dir    = working_dir_parse.group('working_dir')
                view_file_dir  = working_dir_parse.group('view_file_dir')
                view_file_name = working_dir_parse.group('view_file_name')
                arguments = {
                             "working_dir":working_dir,
                             "view_file_dir":view_file_dir,
                             "view_file_name":view_file_name,
                             "file_extension":file_extension,
                             "filepath":filepath
                             }
            elif "py" in file_extension:
                view_file_name     = working_dir_parse.group('view_file_name')
                if "test" in view_file_name:
                    working_dir        = working_dir_parse.group('working_dir')
                    tested_pattern_dir = test_folder.match(filepath)
                    view_file_dir      = tested_pattern_dir.group('pattern_folder')
                    arguments = {
                                 "working_dir":working_dir,
                                 "view_file_dir":view_file_dir,
                                 "view_file_name":view_file_name,
                                 "file_extension":file_extension,
                                 "filepath":filepath
                                 }
                else:
                    working_dir        = working_dir_parse.group('working_dir')
                    tested_pattern_dir = test_folder.match(filepath)
                    # view_file_dir      = tested_pattern_dir.group('pattern_folder')
                    arguments = {
                                 "working_dir":working_dir,
                                 "view_file_dir":working_dir,
                                 "view_file_name":view_file_name,
                                 "file_extension":file_extension,
                                 "filepath":filepath
                                 }
            elif "model" in file_extension:
                expected_model = expected_test_folder.match(filepath)
                actuals_model  =  actuals_test_folder.match(filepath)
                if expected_model:
                    working_dir    = working_dir_parse.group('working_dir')
                    view_file_name = working_dir_parse.group('view_file_name')
                    view_file_dir  = expected_model.group('pattern_folder')
                    arguments = {
                                 "working_dir":working_dir,
                                 "view_file_dir":view_file_dir,
                                 "view_file_name":view_file_name,
                                 "file_extension":file_extension,
                                 "filepath":filepath
                                 }
                elif actuals_model:
                    working_dir    = working_dir_parse.group('working_dir')
                    view_file_name = working_dir_parse.group('view_file_name')
                    view_file_dir  = actuals_model.group('pattern_folder')
                    arguments = {
                                 "working_dir":working_dir,
                                 "view_file_dir":view_file_dir,
                                 "view_file_name":view_file_name,
                                 "file_extension":file_extension,
                                 "filepath":filepath
                                 }
            elif "dml" in file_extension:
                working_dir = working_dir_parse.group('working_dir')
                view_file_name = working_dir_parse.group('view_file_name')
                tested_pattern_dir = dml_test_folder.match(filepath)
                view_file_dir = tested_pattern_dir.group('pattern_folder')
                file_extension = tested_pattern_dir.group('dml_ext')
                arguments = {
                             "working_dir":working_dir,
                             "view_file_dir":view_file_dir,
                             "view_file_name":view_file_name,
                             "file_extension":file_extension,
                             "filepath":filepath
                             }
            elif "tpl" in file_extension:
                working_dir = working_dir_parse.group('working_dir')
                view_file_name = working_dir_parse.group('view_file_name')
                tested_pattern_dir = tpl_pattern_folder.match(filepath)
                view_file_dir = tested_pattern_dir.group('pattern_folder')
                arguments = {
                             "working_dir":working_dir,
                             "view_file_dir":view_file_dir,
                             "view_file_name":view_file_name,
                             "file_extension":file_extension,
                             "filepath":filepath
                             }
        else:
            raise InputError(filepath,"Unsupported file extension!")

        return arguments





class TestTextCommand(sublime_plugin.TextCommand):
    '''
        local_settings IS
            {'BUILDSCRIPTS': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\', 'path_to_move_expected_data': 'D:\\perforce\\addm\\tkn_sandbox\\v.ratniuk\\TH_tools\\move_expected_data.py', 'TKU_PATTERNS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\', 'MIDDLEWAREDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS', 'TKN_MAIN': 'D:\\perforce\\addm\\tkn_main\\', 'DBDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS', 'SANDBOX': 'D:\\perforce\\addm\\tkn_sandbox\\', 'core_path': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\', 'type': 'Local path settings', 'path_to_dan_sublime_modules': 'D:\\perforce\\addm\\tkn_sandbox\\o.danylchenko\\projects\\Notepad_IDE\\Sublime\\TPL_IDE\\bmc_tplpre\\', 'p4_wd': 'D:\\perforce\\', 'path_to_tplpreprocessor': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py', 'SYSTEM': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\SYSTEM'}
        remote_settings IS
            {'view_file_name': 'test', 'addm_dev': '/usr/tideway/TKU/', 'BUILDSCRIPTS': '/usr/tideway/TKU/addm/tkn_main/buildscripts/', 'pattern_dml': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/dml/', 'pattern_actuals': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/actuals/', 'TKU_PATTERNS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/', 'MIDDLEWAREDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/MIDDLEWAREDETAILS/', 'DML_COMMON_PATH': '/usr/tideway/TKU/DML/', 'pattern_test': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/', 'DBDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/DBDETAILS/', 'core_path': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/', 'TKN_MAIN': '/usr/tideway/TKU/addm/tkn_main/', 'TKU_UPLOAD_PATH': '/usr/tideway/TKU/TKU_Upload/', 'TPL_DEV_PATH': '/usr/tideway/TKU/Tpl_DEV/', 'type': 'Remote path settings', 'pattern_expected': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/test/tests/expected/', 'SYSTEM': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/SYSTEM/'}
        current_arguments IS
            {'view_file_name': 'test', 'filepath': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\ApacheHBase\\tests\\test.py', 'python34': 'C:\\Python34', 'python27': 'C:\\Python27', 'working_dir': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\ApacheHBase\\tests', 'plugin_dir': 'C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre', 'view_file_dir': 'ApacheHBase', 'file_extension': 'py', 'result_folder': '\\113'}
    '''
    def run(self, edit):

        settings = ComposeSettings.run(self, edit)

        print("local_settings IS")
        print(settings['local_settings'])

        print("remote_settings IS")
        print(settings['remote_settings'])

        print("current_arguments IS")
        print(settings['current_arguments'])


class TplPreprocCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        """ """
        from bmc_tplpre.check import preproc

        settings = ComposeSettings.run(self, edit)
        args = settings['current_arguments']

        working_dir = args['working_dir']
        view_file_dir = args['view_file_dir']
        view_file_name = args['view_file_name']
        result_folder = args['result_folder']
        plugin_dir = args['plugin_dir']
        filepath = args['filepath']

        print("Run TPLPreprocessor with oprtions:")
        print("working_dir: "+str(working_dir))
        print("view_file_dir: "+str(view_file_dir))
        print("view_file_name: "+str(view_file_name))
        print("result_folder: "+str(result_folder))
        print("plugin_dir: "+str(plugin_dir))
        print("filepath: "+str(filepath))

        preproc.tpl_preprocessor(sublime_working_dir=plugin_dir,
                                 working_dir=working_dir,
                                 dir_label=view_file_dir,
                                 full_curr_path=filepath,
                                 file_path=result_folder)


class SyntaxCheckCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        """ DOC """
        # sys.path.append(os.path.dirname(__file__))

        from bmc_tplpre.check import syntax_checker
        # from bmc_tplpre.check import parse_args


        settings = ComposeSettings.run(self, edit)
        args = settings['current_arguments']

        plugin_dir = args['plugin_dir']
        working_dir = args['working_dir']
        filepath = args['filepath']
        tpl_version_string = '10.2'

        print("Cheking Syntax")
        syntax_passed, msg, result = syntax_checker.syntax_check(
                                                                  curr_work_dir=plugin_dir,
                                                                  working_dir=working_dir,
                                                                  tpl_version=tpl_version_string)
        # message1 = msg[1]['msg']
        # message2 = msg[2]['msg']
        '''
        [{'log': 'debug', 'msg': 'DEBUG: Will check all files in path:                            d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\CAWilyIntroscope'}, {'log': 'error', 'msg': 'ERROR: Tplint cannot run, check if working dir is present!'}, {'log': 'error', 'msg': 'ERROR: Tplint use path:     d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\CAWilyIntroscope\\CAWilyIntroscope.tplpre'}]

        '''

        window = self.view.window()
        message = msg[1]['msg']
        window_msg = window.status_message(message)
        # Popup meessage Windows:
        # err_msg = sublime.error_message(message)
        # HTML popup
        # html_pop = self.view.show_popup(message)

        # parse_args.message_print(msg, log="debug")
        print(message)


class MoveExpectedCommand(sublime_plugin.TextCommand):
    """ """
    def run(self, edit):
        """
           This will start move_expected_data as script in windows env with python34
        """
        settings = ComposeSettings.run(self, edit)
        file_path = settings['current_arguments']['filepath']
        test_new = settings['current_arguments']['working_dir'] + str("\\test_new.py")
        move_expected_py = settings['local_settings']['path_to_move_expected_data']
        python27 = settings['current_arguments']['python27'] + str("\\python.exe")

        test_new_exist = False
        try:
            move = subprocess.Popen('cmd /c ' + python27 +" "+ move_expected_py +" "+ file_path, stdout=subprocess.PIPE)
            move.wait()  # wait until command finished
            test_new_exist = os.path.exists(test_new)  # True
            print("New test file has been created:" + test_new)
        except:
            print("ERROR: TPL_Preprocessor won't run!")

        if test_new_exist:
            view = self.view.window().open_file(test_new)
        else:
            print("File is not exist!")




class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message


# DEPRECATED
'''
This is example or test functions.
Did not used but can be helpful.
'''



class TestWindowCommand(sublime_plugin.WindowCommand):
    '''
    Used to get settings of current open project:

        DOC: https://stackoverflow.com/questions/19524926/get-current-file-name-from-sublime-plugin-windowcommand
        OUTPUT:
        THIS Looks line not so useful BECAUSE I can use TextCommand class to grab all this options.
        Better to forget this approach.
        {'current_dir': ['d:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE', 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles', 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS', 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS', 'D:\\perforce\\addm\\tkn_sandbox\\o.danylchenko\\projects\\Notepad_IDE\\Sublime\\DOCs', 'C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre'], 'project_cfg': 'D:\\Moving\\TPLPRE.sublime-project', 'project_dirs': {'folders': [{'folder_exclude_patterns': ['HarnessFiles', 'tests', 'tpl*', 'Research'], 'file_include_patterns': ['*.tplpre'], 'path': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE'}, {'folder_exclude_patterns': ['HarnessFiles', 'tests', 'tpl*'], 'file_include_patterns': ['*.tplpre'], 'path': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\SupportingFiles'}, {'folder_exclude_patterns': ['HarnessFiles', 'tests', 'tpl*'], 'file_include_patterns': ['*.tplpre'], 'path': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS'}, {'path': 'd:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS'}, {'path': 'D:\\perforce\\addm\\tkn_sandbox\\o.danylchenko\\projects\\Notepad_IDE\\Sublime\\DOCs'}, {'path': 'C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre'}]}, 'filename': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\FujistsuInterstageApplicationServer\\Fujistsu_Interstage_Application_Server.tplpre'}
    '''
    current_settings = ''
    def run(self):
        filename = self.window.active_view().file_name()
        folders_n = self.window.folders()
        project_f = self.window.project_file_name()
        project_d = self.window.project_data()

        current_settings = {
                            "filename":filename,
                            "current_dir":folders_n,
                            "project_cfg":project_f,
                            "project_dirs":project_d
                           }

        # return current_settings
        print(current_settings)




# WORKING!
# https://www.sublimetext.com/docs/3/api_reference.html
# https://forum.sublimetext.com/t/open-file-set-syntax-file/13328

class WindowTestingCommand(sublime_plugin.TextCommand):
    '''
    Window CLASS in TEXT current_settings:
        Sublime settings
            {'addm_dev': '/usr/tideway/TKU', 'python27': 'C:\\Python27\\python.exe', 'python34': 'C:\\Python34\\python.exe', 'tideway_usr': '/usr/tideway', 'p4_wd': 'D:\\perforce'}
        Local path settings
            {'python34': 'C:\\Python34\\python.exe', 'BUILDSCRIPTS': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\', 'path_to_move_expected_data': 'D:\\perforce\\addm\\tkn_sandbox\\v.ratniuk\\TH_tools\\move_expected_data.py', 'python27': 'C:\\Python27\\python.exe', 'SYSTEM': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\SYSTEM', 'MIDDLEWAREDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\MIDDLEWAREDETAILS', 'TKN_MAIN': 'D:\\perforce\\addm\\tkn_main\\', 'DBDETAILS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\DBDETAILS', 'SANDBOX': 'D:\\perforce\\addm\\tkn_sandbox\\', 'core_path': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\', 'type': 'Local path settings', 'path_to_dan_sublime_modules': 'D:\\perforce\\addm\\tkn_sandbox\\o.danylchenko\\projects\\Notepad_IDE\\Sublime\\TPL_IDE\\bmc_tplpre\\', 'path_to_tplpreprocessor': 'D:\\perforce\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py', 'TKU_PATTERNS': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\', 'p4_wd': 'D:\\perforce\\'}
        Remote path settings
            {'addm_dev': '/usr/tideway/TKU/', 'BUILDSCRIPTS': '/usr/tideway/TKU/addm/tkn_main/buildscripts/', 'pattern_dml': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/Fujistsu_Interstage_Application_Server/tests/dml/', 'pattern_actuals': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/Fujistsu_Interstage_Application_Server/tests/actuals/', 'view_file_name': 'Fujistsu_Interstage_Application_Server', 'TKU_PATTERNS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/', 'MIDDLEWAREDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/MIDDLEWAREDETAILS/', 'DML_COMMON_PATH': '/usr/tideway/TKU/DML/', 'pattern_test': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/Fujistsu_Interstage_Application_Server/tests/', 'DBDETAILS': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/DBDETAILS/', 'core_path': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/', 'TKN_MAIN': '/usr/tideway/TKU/addm/tkn_main/', 'TKU_UPLOAD_PATH': '/usr/tideway/TKU/TKU_Upload/', 'TPL_DEV_PATH': '/usr/tideway/TKU/Tpl_DEV/', 'type': 'Remote path settings', 'pattern_expected': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/Fujistsu_Interstage_Application_Server/tests/expected/', 'SYSTEM': '/usr/tideway/TKU/addm/tkn_main/tku_patterns/SYSTEM/'}
        Arguments:
            {'filepath': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\FujistsuInterstageApplicationServer\\Fujistsu_Interstage_Application_Server.tplpre', 'view_file_name': 'Fujistsu_Interstage_Application_Server', 'result_folder': '\\tpl113', 'working_dir': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\FujistsuInterstageApplicationServer', 'view_file_dir': 'FujistsuInterstageApplicationServer', 'plugin_dir': 'C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre'}


        DOC: https://stackoverflow.com/questions/19524926/get-current-file-name-from-sublime-plugin-windowcommand
             https://forum.sublimetext.com/t/open-file-set-syntax-file/13328
    '''
    def run(self, edit):
        filename = self.view.file_name()

        settings_f = self.view.settings().get('bmc_tplpre_settings')

        window = self.view.window()
        window_folders = window.folders()
        window_filename = window.active_view().file_name()
        window_project_file_name = window.project_file_name()

        window_id = window.id()
        window_active_sheet = window.active_sheet()
        window_active_view = window.active_view()

        window_msg = window.status_message("THIS IS MESSAGE!!!!1111")


        print("Curr file :"+filename)
        print("\n\n\nWindow CLASS in TEXT current_settings:")
        print(window_filename)
        print(window_folders)
        print(window_id)
        print(window_active_sheet)
        print(window_active_view)
        print(window_project_file_name)

class MoveExpectedCommand_OLD(sublime_plugin.TextCommand):
    """
        This tries to  execute D:\perforce\addm\tkn_sandbox\v.ratniuk\TH_tools\move_expected_data.py
        With pythin exec funtsion, but prblem is frounded with imports.
        1. Sublime tried to use its own python3.3 Libs.
        2. System installed python34 Lib cannot be imported.
        Error Outputs:
            Executing move_exp_data_file
            Arguments from move_expected_data.py:
            D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\ApacheHBase\\tests\\test.py
            builtins
            Traceback (most recent call last):
              File "C:\\Program Files\\Sublime Text 3\\sublime_plugin.py", line 818, in run_
                return self.run(edit)
              File "C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre\\bmc_tplpre_plugin.py", line 377, in run
                exec(moving, g, l)
              File "<string>", line 97, in <module>
              File "<string>", line 36, in parse
            NameError: global name 're' is not defined
        Locals:
        {'parse': <function parse at 0x0000000009C3AEA0>, 'sys': <module 'sys' (built-in)>, 'test_py_path': 'D:\\perforce\\addm\\tkn_main\\tku_patterns\\CORE\\ApacheHBase\\tests\\test.py', 'json': <module 'json' from 'C:\\Program Files\\Sublime Text 3\\python3.3.zip\\json\\__init__.pyo'>, 'os': <module 'os' from 'C:\\Program Files\\Sublime Text 3\\python3.3.zip\\os.pyo'>, 're': <module 're' from 'C:\\Program Files\\Sublime Text 3\\python3.3.zip\\re.pyo'>, 'save_model': <function save_model at 0x0000000009C3A400>}
        C:\Python34\Lib\
        C:\Python34\Lib\site-packages\
        END of TextCommand RUN

        Modify move_exp_data with:
            print("Arguments from move_expected_data.py:")
            print(test_py_path)
            print(__name__)

            # parse(test_py_path)
            # print("\nGlobals:")
            # print(globals())
            print("\nLocals:")
            print(locals())

    """

    def run(self, edit):
        """ """
        settings = ComposeSettings.run(self, edit)
        file_path = settings['current_arguments']['filepath']
        move_expected_py = settings['local_settings']['path_to_move_expected_data']

        # Python Path: \Lib\site-packages
        python_34 = settings['current_arguments']['python34']
        # C:\Python34\Lib\
        python_modules = python_34+"\\Lib\\"
        # C:\Python34\Lib\site-packages\
        python_third_modules = python_34+"\\Lib\\site-packages\\"

        # from Lib import re
        # from Lib import os
        # from Lib import json
        # from Lib import sys

        print(move_expected_py)
        # import move_expected_py
        # move_expected_py.parse(file_path)


        g = {  }
        # g = { 'test_py_path': file_path}
        # l = { 'test_py_path': file_path, 'full_test_py_path':file_path, '__name__':'__main__' , 'sys.argv':file_path}
        l = { 'test_py_path': file_path}
        # l = { 'test_py_path': file_path, '__name__':'__main__' }
        # l = { 'test_py_path': file_path, 're':re, 'os':os, 'json':json, 'sys':sys}
        print("Doing?")


        moving = open(move_expected_py).read()
        exec(moving, g, l)

        # move_expected_data(self, edit)

        print(python_modules)
        print(python_third_modules)
        print("END of TextCommand RUN")


    def move_expected_data(self, edit):

        import re
        import os
        import json
        import sys

        settings = ComposeSettings.run(self, edit)
        file_path = settings['current_arguments']['filepath']
        move_expected_py = settings['local_settings']['path_to_move_expected_data']

        g = {  }
        # g = { 'test_py_path': file_path}
        g = { 'test_py_path': file_path, '__name__':'__main__' }
        # l = { 'test_py_path': file_path, 'full_test_py_path':file_path }
        print("Doing?")


        moving = open(move_expected_py).read()
        exec(moving, g, {})