"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""


import os
import re
import subprocess
import datetime


'''
1. If syntax_passed = True after Notepad_IDE/Sublime/check/syntax_checker.py run TPLPreprocessor (input)
2. Run TPLPreprocessor with passed args - "with imports/without", "tpl ver"  (input)
3. Check if TPLPreprocessor finished its work, check results update - tpl_preproc = False\True
4. Return Tplpreproc result (tpl_preproc = False/True) and folder path (output)
'''


# noinspection PyBroadException
class Preproc:

    def __init__(self, logging):

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
            log.debug("Got the p4 workspace path from 'full_path_parse()' "
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

    def tpl_preprocessor(self, workspace, input_path, output_path, mode):
        """
        Run TPLPreprocessor in two scenarios:
        1. If IMPORT or RECURSIVE_IMPORT - then run in folder passed as arg.
        2. If NOT - run only on current file.


        :param workspace: str
        :param input_path:  What to preproc file\folder
        :param output_path: Where to output pattern folder or imports folder
        :param mode: imports \ recursive imports
        :return: True\False
        """
        _, t_pre = self.find_tplpreprocessor(workspace)
        # print(t_pre)

        log = self.logging
        log.debug("Using script path as: " + t_pre)

        tpl_preproc = False
        python_v = "C:\\Python27\\python.exe"
        # log.debug("Using TPLPreprocessor from: " + str(t_pre))

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

                            tpl_result_files = os.listdir(output_path+os.sep+folder)
                            for file in tpl_result_files:
                                file_time = os.path.getmtime(output_path+os.sep+folder+os.sep+file)
                                now = datetime.datetime.now()
                                ago = now - datetime.timedelta(minutes=5)
                                file_time_stamp = datetime.datetime.fromtimestamp(file_time)
                                if file_time_stamp < ago:
                                    log.warn("TPLPreprocessor result files looks like older that 5 min. "
                                             "Please check: " + str(file_time_stamp))
                                if file_time_stamp > ago:
                                    log.debug("TPLPreprocessor result files are recent: " + str(file_time_stamp))
                                    tpl_preproc = os.path.exists(output_path)  # True
                                # Probably no need to check each folder, if one is recent, then Preproc was run.
                                break
                            break
                    if tpl_preproc:
                        log.debug("TPLPreprocessor success: " + output_path)
                except:
                    log.error("TPL_Preprocessor won't run! "
                              "Check paths, user rights and logs. Try to execute preproc from cmd.")
            else:
                log.error("Path is not exist. TPLPreprocessor won't run! " + str(input_path))

        elif mode == "recursive_imports":
            # NO IMPORTS - run on folder
            log.debug("python2.7 : TPLPreprocessor run all on all files in directory: " + input_path)
            log.debug("Running in recursive_imports mode! "
                      "It means - will process all files found in working folder.")
            if os.path.exists(input_path):
                try:
                    run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "' + t_pre + '" -q -d "' + input_path + '"',
                                                   stdout=subprocess.PIPE)
                    run_preproc.wait()  # wait until command finished

                    # result = run_preproc.stdout.read().decode()

                    folder_content = os.listdir(output_path)
                    for folder in folder_content:
                        if re.match("tpl\d+", folder) is not None:

                            tpl_result_files = os.listdir(output_path+os.sep+folder)
                            for file in tpl_result_files:
                                file_time = os.path.getmtime(output_path+os.sep+folder+os.sep+file)
                                now = datetime.datetime.now()
                                ago = now - datetime.timedelta(minutes=15)
                                file_time_stamp = datetime.datetime.fromtimestamp(file_time)

                                if file_time_stamp < ago:

                                    log.warn("TPLPreprocessor result files looks like older that 15 min. "
                                             "Please check: " + str(file_time_stamp))

                                if file_time_stamp > ago:

                                    log.debug("TPLPreprocessor result files are recent: " + str(file_time_stamp))
                                    tpl_preproc = os.path.exists(output_path)  # True
                                # Probably no need to check each folder, if one is recent, then Preproc was run.
                                break
                            break
                    if tpl_preproc:
                        log.debug("TPLPreprocessor success: " + output_path)
                except:
                    log.error("TPL_Preprocessor won't run! "
                              "Check paths, user rights and logs. Try to execute preproc from cmd.")
            else:
                log.error("Path is not exist. TPLPreprocessor won't run! " + str(input_path))

        elif mode == "solo_mode":
            # SOLO MODE - nothing will be processed - only active pattern.
            log.debug("python2.7 : TPLPreprocessor run all on one file " + input_path)
            log.debug("Solo mode - only active file will be processed!")
            if os.path.exists(input_path):
                try:
                    run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "' + t_pre + '" -q -f "' + input_path + '"',
                                                   stdout=subprocess.PIPE)
                    run_preproc.wait()  # wait until command finished

                    # result = run_preproc.stdout.read().decode()

                    folder_content = os.listdir(output_path)
                    for folder in folder_content:
                        if re.match("tpl\d+", folder) is not None:

                            tpl_result_files = os.listdir(output_path+os.sep+folder)
                            for file in tpl_result_files:
                                file_time = os.path.getmtime(output_path+os.sep+folder+os.sep+file)
                                now = datetime.datetime.now()
                                ago = now - datetime.timedelta(minutes=15)
                                file_time_stamp = datetime.datetime.fromtimestamp(file_time)
                                if file_time_stamp < ago:
                                    log.warn("TPLPreprocessor result files looks like older that 15 min. "
                                             "Please check: " + str(file_time_stamp))
                                if file_time_stamp > ago:
                                    log.debug("TPLPreprocessor result files are recent: " + str(file_time_stamp))
                                    tpl_preproc = os.path.exists(output_path)  # True
                                # Probably no need to check each folder, if one is recent, then Preproc was run.
                                break
                            break
                    if tpl_preproc:
                        log.debug("TPLPreprocessor success: " + output_path)
                except:
                    log.error("TPL_Preprocessor won't run! "
                              "Check paths, user rights and logs. Try to execute preproc from cmd.")
            else:
                log.error("Path is not exist. TPLPreprocessor won't run! " + str(input_path))

        return tpl_preproc
