"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""


import os
import re
import sys
import subprocess
import datetime


'''
1. If syntax_passed = True after Notepad_IDE/Sublime/check/syntax_checker.py run TPLPreprocessor (input)
2. Run TPLPreprocessor with passed args - "with imports/without", "tpl ver"  (input)
3. Check if TPLPreprocessor finished its work, check results update - tpl_preproc = False\True
4. Return Tplpreproc result (tpl_preproc = False/True) and folder path (output)
'''


class Preproc:

    def __init__(self, logging):
        # TODO: Clear out fake code, make simpler, logic is almost done.

        self.logging = logging
        self.sublime_working_dir = os.path.dirname(os.path.abspath(__file__))
        # sublime_working_dir = "C:\\Users\\o.danylchenko\\AppData\\Roaming\\Sublime Text 3\\Packages\\bmc_tplpre"

    def find_tplpreprocessor(self, workspace):
        """
        This will find //addm/tkn_main/buildscripts/TPLPreprocessor.py

        :type workspace: path to p4 workspace - from -full_path arg
        :return: tpl_preproc_location
        """
        log = self.logging

        if workspace:
            log.debug("Got the p4 workspase path from 'full_path_parse()' "
                      "and will try to locate TPLPreprocessor: " + workspace)

            # tpl_preproc_location = workspace + "\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py"
            tpl_preproc_dir = workspace + "\\addm\\tkn_main\\buildscripts\\"
            tpl_preproc_py = workspace + "\\addm\\tkn_main\\buildscripts" + os.sep + "TPLPreprocessor.py"
            tpl_preproc_py_check = os.path.exists(tpl_preproc_dir + os.sep + "TPLPreprocessor.py")

            if os.path.exists(tpl_preproc_py_check):
                log.debug("TPLPreprocessor found in folder: " + tpl_preproc_dir)
                return tpl_preproc_dir, tpl_preproc_py
            else:
                log.warn("TPLPreprocessor.py file is not found in path: " + str(tpl_preproc_py))
        else:
            log.warn("Cannot run without p4 workspace path. Check args.")

    def read_tplpreprocessor(self, tpl_preproc_dir):
        """

        Will try to import class TPLPreprocessor and use it as normal py module;
         - https://stackoverflow.com/questions/42171786/import-class-from-another-directory
        Get from it some args;

        Some args:

            knownADDMVersions
            knownTPLVersions
            previouslySupportedTPLVersions
            supportedTPLVersions
            supportedADDMVersions

        :return:
        """

        log = self.logging

        if tpl_preproc_dir:
            log.debug("TPLPreprocessor.py is on place - continue..." + str(tpl_preproc_dir))

            import sys
            sys.path.insert(1, os.path.join(sys.path[0], tpl_preproc_dir))

            from TPLPreprocessor import TPLPreprocessor
            from TPLPreprocessor import main

            # TPLPreprocessor()
            tpl_preprocessor_class = TPLPreprocessor()
            tpl_preprocessor_main = main

            known_addm_ver = tpl_preprocessor_class.knownADDMVersions
            known_tpl_ver = tpl_preprocessor_class.knownTPLVersions

            supported_addm_ver = tpl_preprocessor_class.supportedTPLVersions
            supported_tpl_ver = tpl_preprocessor_class.supportedADDMVersions

            log.info("TPLPreprocessor knownADDMVersions: " + str(known_addm_ver))
            log.info("TPLPreprocessor knownTPLVersions: " + str(known_tpl_ver))

            log.info("TPLPreprocessor supportedTPLVersions: " + str(supported_addm_ver))
            log.info("TPLPreprocessor supportedADDMVersions: " + str(supported_tpl_ver))

            return tpl_preprocessor_class, tpl_preprocessor_main, supported_addm_ver, supported_tpl_ver

        else:
            log.warn("There is no TPLPreprocessor.py file found. Please check it in path: " + tpl_preproc_dir)

    def tpl_preprocessor_new(self, tpl_preproc_py, tpl_preprocessor_obj, full_path_args_dict):
        """
        :param tpl_preproc_py: TPLPreprocessor.py
        :param tpl_preprocessor_obj: imported TPLPreprocessor instance.
        :type full_path_args_dict: dict of previously parsed settings from full pattern path.
        """

        log = self.logging

        args = full_path_args_dict
        tpl_preprocessor_work_path = args['working_dir']
        tpl_preprocessor_output_path = args['working_dir']
        single_pattern_path = args['working_dir'] + os.sep + args['file_name'] + "." + args['file_ext']

        log.debug("single_pattern_path: " + single_pattern_path)

        args_string = "-d " + tpl_preprocessor_work_path + "-o " + tpl_preprocessor_output_path

        # g = {'preproc_py': tpl_preproc_py, 'proposedHomeDirectory': tpl_preprocessor_work_path}
        g = {'TEST': tpl_preprocessor_work_path,
             'self.tplpreFileFullPaths': tpl_preprocessor_work_path,
             '__name__': '__main__',
             'sys': sys,
             'os': os}
        l = {'TEST': tpl_preprocessor_work_path, 'self.tplpreFileFullPaths': tpl_preprocessor_work_path, '__name__':'__main__'}

        # g = {'preproc_py': tpl_preproc_py, 'argv': args_string}
        # l = {'preproc_py': tpl_preproc_py, 'proposedHomeDirectory': tpl_preprocessor_work_path}

        preproc_read = open(tpl_preproc_py).read()
        exec(preproc_read, g, {})

        # if tpl_preprocessor_obj:
        #
        #     log.debug("TPLPreprocessor is ready to run.")
        #     log.debug("TPLPreprocessor is imported as: " + str(type(tpl_preprocessor_obj)))
        #
        #     if tpl_preprocessor_work_path:
        #
        #         log.debug("tpl_preprocessor_work_path: " + tpl_preprocessor_work_path)
        #
        #         if tpl_preprocessor_output_path:
        #
        #             log.info("TPLPreprocessor output directory is set. Will see tpl files in there.")
        #             log.debug("tpl_preprocessor_output_path: " + tpl_preprocessor_output_path)
        #
        #             import sys
        #             # tpl_preprocessor_obj.initialise(sys.argv["-d" + tpl_preprocessor_work_path])
        #             # tpl_preprocessor_obj.initialise(sys.argv[1])
        #             # tpl_preprocessor_obj.initialise("-h")
        #             # tpl_preprocessor_obj.main(arg1, arg2)
        #             sys.argv = []
        #             # sys.argv.append("-h")
        #             # sys.argv.append(tpl_preproc_dir+"TPLPreprocessor.py")
        #             # sys.argv.append('-d '+tpl_preprocessor_work_path)
        #             # sys.argv.append('-o '+tpl_preprocessor_work_path)
        #             tpl_preprocessor_obj.tplpreFileFullPaths = [single_pattern_path]
        #             log.debug("tpl_preprocessor_obj.tplpreFileFullPaths: " + str(tpl_preprocessor_obj.tplpreFileFullPaths))
        #             tpl_preprocessor_obj()
        #
        #         else:
        #             log.info("TPLPreprocessor output directory is not set. WIll output in current file path.")
        #     else:
        #         log.warn("TPLPreprocessor wouldn't run without path to file or folder with .tplpre file(s)")
        # else:
        #     log.warn("TPLPreprocessor is probably was not imported correctly.")

    def tpl_preprocessor(self, workspace, input_path, output_path, mode):
        """
        Run TPLPreprocessor in two scenarios:
        1. If IMPORT or RECURSIVE_IMPORT - then run in folder passed as arg.
        2. If NOT - run only on current file.


        :param input_path:  What to preproc file\folder
        :param output_path: Where to output pattern folder or imports folder
        :param mode: imports \ recursise imports
        :return: True\False
        """

        _, t_pre = self.find_tplpreprocessor(workspace)
        # print(t_pre)

        log = self.logging
        log.debug("Using script path as: " + t_pre)

        tpl_preproc = False
        python_v = "C:\\Python27\\python.exe"
        log.debug("Using TPLPreprocessor from: " + str(t_pre))

        if mode == "usual_imports":
            log.info("python2.7 : TPLPreprocessor run on one file: " + input_path)
            log.debug("Running in usual_imports mode!")
            if os.path.exists(input_path):
                try:
                    run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "'
                                                   + t_pre + '" -q -o "' + output_path + '" -f "' + input_path + '"',
                                                   stdout=subprocess.PIPE)
                    run_preproc.wait()  # wait until command finished
                    folder_content = os.listdir(output_path)
                    for folder in folder_content:
                        if re.match("tpl\d+", folder) is not None:
                            folder_creation_time = os.path.getctime(output_path+os.sep+folder)
                            now = datetime.datetime.now()
                            ago = now - datetime.timedelta(minutes=15)
                            folder_time = datetime.datetime.fromtimestamp(folder_creation_time)
                            if folder_time < ago:
                                log.warn("TPLPreprocessor result folders looks like older that 15 min. Please check: + "
                                         + str(folder_time))
                            if folder_time > ago:
                                log.debug("TPLPreprocessor result folders are recent: " + str(folder_time))
                                tpl_preproc = os.path.exists(output_path)  # True
                                break  # Probably no need to check each folder, if one is recent, then Preproc was run.
                    if tpl_preproc:
                        log.debug("TPLPreprocessor success: " + output_path)
                except:
                    log.error("TPL_Preprocessor won't run!")
            else:
                log.error("Path is not exist. TPLPreprocessor won't run! " + str(input_path))
        elif mode == "recursive_imports":
        # NO IMPORTS - run on folder
            log.debug("python2.7 : TPLPreprocessor run all on all files in directory: " + input_path)
            log.debug("Running in recursive_imports mode! Which means - it will process all files found in working folder.")
            if os.path.exists(input_path):
                try:
                    run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "' + t_pre + '" -q -d "' + input_path + '"',
                                                   stdout=subprocess.PIPE)
                    run_preproc.wait()  # wait until command finished
                    result = run_preproc.stdout.read().decode()
                    # print(result)
                    folder_content = os.listdir(output_path)
                    for folder in folder_content:
                        if re.match("tpl\d+", folder) is not None:
                            folder_creation_time = os.path.getctime(output_path+os.sep+folder)
                            now = datetime.datetime.now()
                            ago = now - datetime.timedelta(minutes=15)
                            folder_time = datetime.datetime.fromtimestamp(folder_creation_time)
                            if folder_time < ago:
                                log.warn("TPLPreprocessor result folders looks like older that 15 min. Please check: + "
                                         + str(folder_time))
                            if folder_time > ago:
                                log.debug("TPLPreprocessor result folders are recent: " + str(folder_time))
                                tpl_preproc = os.path.exists(output_path)  # True
                                break  # Probably no need to check each folder, if one is recent, then Preproc was run.
                    if tpl_preproc:
                        log.debug("TPLPreprocessor success: " + output_path)
                except:
                    log.error("TPL_Preprocessor won't run!")
            else:
                log.error("Path is not exist. TPLPreprocessor won't run! " + str(input_path))

        return tpl_preproc

    def tpl_preprocessor_pack(self, file_path_args, mode):
        """
        Run TPLPreprocessor in two scenarios:
        1. If IMPORT or RECURSIVE_IMPORT - then run in folder passed as arg.
        2. If NOT - run only on current file.


        :param file_path_args:  WD where pattern lies
        :param mode: Name of WD
        :return: True\False
        """

        log = self.logging
        log.debug("Using script path as: " + self.sublime_working_dir)

        tpl_preproc = False
        python_v = "C:\\Python27\\python.exe"
        log.debug("Using TPLPreprocessor from: " + str(self.sublime_working_dir))


        # NO IMPORTS - run on folder

        log.debug("python2.7 : TPLPreprocessor run all on all files in directory: " + dir_label)
        try:
            run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "'
                                           + self.sublime_working_dir + '\\TPLPreprocessor.py" -q -o "'
                                           + working_dir + '" -d "' + working_dir + '"', stdout=subprocess.PIPE)
            run_preproc.wait()  # wait until command finished
            tpl_preproc = os.path.exists(file_path)  # True
            if tpl_preproc:
                log.debug("TPLPreprocessor success: " + file_path)
        except:
            log.error("TPL_Preprocessor won't run!")

        return tpl_preproc