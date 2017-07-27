import os
import subprocess

from check.logger import i_log

log = i_log(level='DEBUG', name=__name__)

'''
1. If syntax_passed = True after Notepad_IDE/Sublime/check/syntax_checker.py run TPLPreprocessor (input)
2. Run TPLPreprocessor with passed args - "with imports/without", "tpl ver"  (input)
3. Check if TPLPreprocessor finished its work, check results update - tpl_preproc = False\True
4. Return Tplpreproc result (tpl_preproc = False/True) and folder path (output)
'''


def find_tplpreprocessor(workspace):
    """
    This will find //addm/tkn_main/buildscripts/TPLPreprocessor.py

    :type workspace: path to p4 workspace - from -full_path arg
    :return: tpl_preproc_location
    """

    if workspace:
        log.debug("Got the p4 workspase path from 'full_path_parse()' "
                  "and will try to locate TPLPreprocessor: " + workspace)

        # tpl_preproc_location = workspace + "\\addm\\tkn_main\\buildscripts\\TPLPreprocessor.py"
        tpl_preproc_dir = workspace + "\\addm\\tkn_main\\buildscripts\\"
        tpl_preproc = os.path.exists(tpl_preproc_dir)
        if tpl_preproc:
            log.debug("TPLPreprocessor found in folder: " + tpl_preproc_dir)
            return tpl_preproc_dir

    else:
        log.warn("Cannot run without p4 workspace path. Check args.")


def read_tplpreprocessor(tpl_preproc_dir):
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

    if tpl_preproc_dir:
        log.debug("Got the dir to TPLPreprocessor.py - checking file.")

        # tpl_preproc_location = tpl_preproc_dir + "TPLPreprocessor.py"
        tpl_preproc_py = os.path.exists(tpl_preproc_dir)

        if tpl_preproc_py:
            log.debug("TPLPreprocessor.py is on place - continue...")

            import sys
            sys.path.insert(1, os.path.join(sys.path[0], tpl_preproc_dir))

            from TPLPreprocessor import TPLPreprocessor

            TPLPreprocessor()
            tpl_preprocessor_class = TPLPreprocessor()

            known_addm_ver = tpl_preprocessor_class.knownADDMVersions
            known_tpl_ver = tpl_preprocessor_class.knownTPLVersions

            supported_addm_ver = tpl_preprocessor_class.supportedTPLVersions
            supported_tpl_ver = tpl_preprocessor_class.supportedADDMVersions
            #
            # print(tpl_ver)
            #
            log.info("TPLPreprocessor knownADDMVersions: " + str(known_addm_ver))
            log.info("TPLPreprocessor knownTPLVersions: " + str(known_tpl_ver))

            log.info("TPLPreprocessor supportedTPLVersions: " + str(supported_addm_ver))
            log.info("TPLPreprocessor supportedADDMVersions: " + str(supported_tpl_ver))

        else:
            log.warn("There is no TPLPreprocessor.py file found. Please check it in path: " + tpl_preproc_dir)
    else:
        log.warn("Path to TPLPreprocessor file is empty!")


def tpl_preprocessor(sublime_working_dir, working_dir, dir_label, full_curr_path, file_path):
    """
    1. If preproc has an argument full_curr_path - the path to edited pattern:
        RUN only on this pattern and include imports from it.

    2. If preproc has NO full_curr_path - RUN on the active folder, where edited pattern situated, no imots included.

    :param sublime_working_dir: Working dir where sublime plugin and this module lies
    :param working_dir:  WD where pattern lies
    :param dir_label: Name of WD
    :param full_curr_path: full path to edited pattern
    :param file_path: result folder after TPLPreproc run
    :return: True\False
    """

    tpl_preproc = False
    python_v = "C:\\Python27\\python.exe"
    log.debug("Using TPLPreprocessor from: " + str(sublime_working_dir))

    if full_curr_path:
        log.info("python2.7 : TPLPreprocessor run on one file: "  + full_curr_path)
        try:
            run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "'
                                           + sublime_working_dir + '\\TPLPreprocessor.py" -q -o "'
                                           + working_dir + '" -f "' + full_curr_path + '"', stdout=subprocess.PIPE)
            run_preproc.wait()  # wait until command finished
            tpl_preproc = os.path.exists(file_path)  # True
            if tpl_preproc:
                log.debug("TPLPreprocessor success: " + file_path)
        except:
            log.error("TPL_Preprocessor won't run!")
    # NO IMPORTS - run on folder
    else:
        log.debug("python2.7 : TPLPreprocessor run all on all files in directory: " + dir_label)
        try:
            run_preproc = subprocess.Popen('cmd /c ' + python_v + ' "'
                                           + sublime_working_dir + '\\TPLPreprocessor.py" -q -o "'
                                           + working_dir + '" -d "' + working_dir + '"', stdout=subprocess.PIPE)
            run_preproc.wait()  # wait until command finished
            tpl_preproc = os.path.exists(file_path)  # True
            if tpl_preproc:
                log.debug("TPLPreprocessor success: " + file_path)
        except:
            log.error("TPL_Preprocessor won't run!")

    return tpl_preproc
