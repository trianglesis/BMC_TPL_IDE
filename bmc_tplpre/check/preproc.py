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
import logging

log = logging.getLogger("check.logger")

'''
1. If syntax_passed = True after Notepad_IDE/Sublime/check/syntax_checker.py run TPLPreprocessor (input)
2. Run TPLPreprocessor with passed args - "with imports/without", "tpl ver"  (input)
3. Check if TPLPreprocessor finished its work, check results update - tpl_preproc = False\True
4. Return Tplpreproc result (tpl_preproc = False/True) and folder path (output)
'''


# noinspection PyBroadException
class Preproc:

    def __init__(self):
        """
            This could initialize some vars here. Later.

        """
        log.debug("Starting Preprocessor.")

    @staticmethod
    def find_tplpreprocessor(workspace):
        """
        This will find //addm/tkn_main/buildscripts/TPLPreprocessor.py

        :type workspace: path to p4 workspace - from -full_path arg
        :return: tpl_preproc_location
        """

        if workspace:
            # log.debug("Got p4 workspace path from 'full_path_parse()' try to locate TPLPreprocessor: " + workspace)
            # tpl_preproc_location = workspace + "\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py"

            tpl_preproc_dir = workspace + "\\addm\\tkn_main\\buildscripts\\"
            tpl_preproc_py = workspace + "\\addm\\tkn_main\\buildscripts" + os.sep + "TPLPreprocessor.py"
            tpl_preproc_py_check = tpl_preproc_dir + os.sep + "TPLPreprocessor.py"

            if os.path.exists(tpl_preproc_py_check):
                log.debug("TPLPreprocessor found in folder: " + tpl_preproc_dir)
            else:
                log.warning("TPLPreprocessor.py file is not found in path: " + str(tpl_preproc_py))
                raise Exception("Preprocessor wasn't found on its usual place: "+str(tpl_preproc_dir))
        else:
            raise Exception("Cannot run without p4 workspace path. Check args.")

        return tpl_preproc_dir, tpl_preproc_py

    @staticmethod
    def results_parse(cmd, run_preproc, output_path, tpl_preproc):
        """
        Check timestamp of files after Preproc. If older than 5 min - log error.

        :return:
        """

        stdout, stderr = run_preproc.communicate()
        run_preproc.wait()  # wait until command finished

        # result = stdout.decode('UTF-8').rstrip('\r|\n')
        err_result = stderr.decode('UTF-8').rstrip('\r|\n')

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
                        log.warning("TPLPreprocessor result files looks like older that 5 min. "
                                    "Please check: " + str(file) + " time: " + str(file_time_stamp))

                    if file_time_stamp > ago:
                        log.debug("TPLPreprocessor result files are recent: " + str(file_time_stamp))
                        tpl_preproc = os.path.exists(output_path)  # True
                    # Probably no need to check each folder, if one is recent, then Preproc was run.
                    break
                break
        if tpl_preproc:
            log.debug("TPLPreprocessor success: " + output_path)
        if err_result:
            log.debug("Preproc cmd: "+str(cmd))
            raise Exception("Preproc cannot run, please check input args and paths. More info in debug mode."
                            "While TPLPreproc - this error occurs: "+str(err_result))

    def run_preproc_cmd(self, cmd, output_path):
        """
        Input cmd string.
        Execute subprocess.
        Parse results.

        :param output_path: str
        :param cmd: str
        :return:
        """
        tpl_preproc = False
        try:
            run_preproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.results_parse(cmd, run_preproc, output_path, tpl_preproc)
            tpl_preproc = True

        except IOError as e:
            raise IOError("TPL Preproc cannot run with current options: "+str(cmd)+" with error: "+str(e))

        except:
            raise Exception("TPL_Preprocessor won't run! "
                            "Check paths, user rights and logs. Try to execute preproc from cmd.")
        return tpl_preproc

    def tpl_preprocessor(self, workspace, input_path, output_path, mode):
        """
        Run TPLPreprocessor in two scenarios:
        1. If IMPORT or RECURSIVE_IMPORT - then run in folder passed as arg.
        2. If NOT - run only on current file.

        # Active tests:
        Run mode and result True
        >>> Preproc().tpl_preprocessor(workspace="d:\\\\perforce",
        ...                            input_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\BMCRemedyARSystem.tplpre",
        ...                            output_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\",
        ...                            mode="usual_imports")
        True

        Run mode and result True
        NOTE: This test should have imports folder after imports run, in othr way it fails.
        >>> Preproc().tpl_preprocessor(workspace="d:\\\\perforce",
        ...                            input_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\imports",
        ...                            output_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\imports",
        ...                            mode="recursive_imports")
        True

        Run mode and result True
        >>> Preproc().tpl_preprocessor(workspace="d:\\\\perforce",
        ...                            input_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\BMCRemedyARSystem.tplpre",
        ...                            output_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\",
        ...                            mode="solo_mode")
        True

        # Fail tests
        Run unsupported args and Traceback:
        >>> Preproc().tpl_preprocessor(workspace="d:\\\\perforce",
        ...                            input_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\BMCRemedyARSystem.tpl",
        ...                            output_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\",
        ...                            mode="usual_imports")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        Exception: This is not a tplpre file. TPLPreprocessor won't run! - d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\BMCRemedyARSystem.tpl

        Run unsupported args and Traceback:
        >>> Preproc().tpl_preprocessor(workspace="d:\\\\perforce",
        ...                            input_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\",
        ...                            output_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\",
        ...                            mode="recursive_imports")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        Exception: This is not a tplpre file. TPLPreprocessor won't run! - d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\BMCRemedyARSystem.tpl

        Run unsupported args and Traceback:
        >>> Preproc().tpl_preprocessor(workspace="d:\\\\perforce",
        ...                            input_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\BMCRemedyARSystem.tpl",
        ...                            output_path="d:\\\\perforce\\\\addm\\\\tkn_main\\\\tku_patterns\\\\CORE\\\\"
        ...                            "BMCRemedyARSystem\\\\",
        ...                            mode="solo_mode")
        ... # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        Exception: This is not a tplpre file. TPLPreprocessor won't run! - d:\perforce\addm\tkn_main\tku_patterns\CORE\BMCRemedyARSystem\BMCRemedyARSystem.tpl


        :param workspace: str
        :param input_path:  What to preproc file\folder
        :param output_path: Where to output pattern folder or imports folder
        :param mode: imports \ recursive imports
        :return: True\False
        """
        tpl_preproc = False

        python_v = "C:\\Python27\\python.exe"
        _, t_pre = self.find_tplpreprocessor(workspace)
        pre_cmd = "cmd /c " + python_v + " " + t_pre + " -q "
        output_arg = ' -o "'+output_path+'"'

        if mode == "usual_imports":
            log.debug("python2.7 : TPLPreprocessor file: " + input_path)
            log.info("Running in usual_imports mode!")

            if os.path.isfile(input_path) and input_path.endswith('.tplpre'):
                # Single file and output with imports:
                input_arg = ' -f "'+input_path+'"'
                cmd = pre_cmd+output_arg+input_arg
                tpl_preproc = self.run_preproc_cmd(cmd, output_path)
            else:
                raise Exception("This is not a tplpre file. TPLPreprocessor won't run! - " + str(input_path))

        elif mode == "recursive_imports":
            # NO IMPORTS - run on folder
            log.debug("python2.7 : TPLPreprocessor all files in: " + input_path)
            log.info("Running in recursive_imports mode!")

            if os.path.isdir(input_path) and input_path.endswith('imports'):
                # All files in active or imports folder:
                input_arg = ' -d "'+input_path+'"'
                cmd = pre_cmd+input_arg

                tpl_preproc = self.run_preproc_cmd(cmd, output_path)
            else:
                raise Exception("This is not an 'imports' folder. TPLPreprocessor won't run! - " + str(input_path))

        elif mode == "solo_mode":
            # SOLO MODE - nothing will be processed - only active pattern.
            log.debug("python2.7 : TPLPreprocessor single file: " + input_path)
            log.info("Solo mode!")

            if os.path.isfile(input_path) and input_path.endswith('.tplpre'):
                # Only active file in active folder.
                input_arg = ' -f "'+input_path+'"'
                cmd = pre_cmd+input_arg

                tpl_preproc = self.run_preproc_cmd(cmd, output_path)
            else:
                raise Exception("This is not a tplpre file. TPLPreprocessor won't run! - " + str(input_path))

        return tpl_preproc
