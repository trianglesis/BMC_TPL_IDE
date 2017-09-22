"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import subprocess
import re
import sys
import os
import logging
import time

try:
    import progressbar
except ModuleNotFoundError:
    progressbar = ''
    pass
except ImportError:
    progressbar = ''
    pass

log = logging.getLogger("check.logger")

'''
1. Use working dir and tpl ver and run syntax check (input)
2. Save syntax check result
2.1 If pass - update var with syntax_passed = True
2.2 If fail syntax_passed = Fail
3. Return syntax check results
'''
# TODO: Make another syntax checking procedure maybe on python AST.


class SyntaxCheck:
    """
        Verify if tplint is present on current system.
        If not - use something another to check common errors and typos in tpl\\tplpre files.
        to be continued...

        If tplint is present - use arg from ask_addm to compare the version of tpl which addm support.
        Run check.
    """

    def __init__(self):
        """
        """

        # NOTE: tplint was updated in 2016 last time, so we can use only versions not greater then 11.0
        # Maybe I can spend some time to update it to recent versions in future.
        self.SYNTAX_SUPPORTED = {
                                 # '11.2': 'CustardCream',
                                 # '11.1': 'Bobblehat',
                                 '11.0': 'Aardvark',
                                 '10.2': 'Zythum',
                                 '10.1': 'Zed',
                                 '10.0': 'Yodel'
                                 }

    def syntax_check(self, working_dir, disco_ver):
        """
        Check the syntax in working dir for all found files.
        Tpl version for check will be used from ADDM.
        If no ADDM ip was added in args - will latest available hardcoded.

        Until tplint updated - it can check syntax only for max version 10.2.

        :param disco_ver: str
        :param working_dir: str
        :return:
        """

        # TODO: Add progressbar:
        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stderr()
            bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        tpl_mod_dir = os.path.abspath(os.path.join(__file__ , "../.."))
        syntax_passed = False

        # errors_re = re.compile("\s+Errors:\s+(.+)")
        # mod_re = re.compile("Module:\s+(.+)")

        match_result = re.compile("(?P<error>\w+\s\w+) at or near '(?P<near>\S+)', "
                                  "line (?P<line>\d+), in (?P<module>\S+)")

        log.debug("Syntax: Will check all files in path: " + str(working_dir))

        if disco_ver not in self.SYNTAX_SUPPORTED:
            log.info("NOTE: tplint was updated in 2016 last time, "
                     "so we can use only version which is not greater then 11.0")
            disco_ver = 11.0

        # noinspection PyBroadException
        try:
            log.debug("Syntax: Checking syntax. Options: --discovery-versions="+str(disco_ver) +
                      " --loglevel=WARN"+" -t "+tpl_mod_dir+" in: "+str(working_dir))

            open_path = subprocess.Popen('"' + tpl_mod_dir + '\\tplint\\tplint.exe"'
                                                             ' --discovery-versions='+str(disco_ver) +
                                         ' --loglevel=WARN'
                                         ' -t "'+tpl_mod_dir+'\\taxonomy\\00taxonomy.xml"',
                                         cwd=working_dir,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)

            stdout, stderr = open_path.communicate()
            open_path.wait()  # wait until command finished

            result = stdout.decode('UTF-8').rstrip('\r|\n')
            err_result = stderr.decode('UTF-8').rstrip('\r|\n')

            # result = open_path.stdout.read().decode()
            if "No issues found!" in result:
                log.info("\t\tBuild OK: Syntax: PASSED!")
                syntax_passed = True
            elif match_result.findall(result):
                # error_modules = mod_re.findall(result)
                # errors = errors_re.findall(result)
                log.error("Syntax: ERROR: Some issues found!""\n" + str(result))
            else:
                log.error("Syntax: Something is not OK \n" + str(result))

            if err_result:
                log.error("This error occurs while executing syntax check: "+str(err_result))
        except:
            log.error("Syntax: Tplint cannot run, check if working dir is present!")
            log.error("Syntax: Tplint use path: " + tpl_mod_dir)

        # bar.finish()
        return syntax_passed

    @staticmethod
    def parse_syntax_result(result):
        """
        This will output errors in STDERR for tplint only.

        :param result:
        :return:
        """
        match_result = re.compile("(?P<error>\w+\s\w+) at or near"
                                  " '(?P<near>\S+)', line (?P<line>\d+), in (?P<module>\S+)")
        used_mod_re = re.compile("Module:\s(\S+)\s\s+Errors:")
        # noinspection SpellCheckingInspection
        error_re = re.compile("Errors:\s+(.*)\sat\sor\snear ")

        if "No issues found!" in result:
            sys.stdout.write("No issues found!")
        if "Errors" in result:
            parsed_output = match_result.findall(result)
            used_mod = used_mod_re.findall(result)
            errors = error_re.findall(result)
            if parsed_output and used_mod:

                for item in parsed_output:
                    error = ("Found errors \'" + str(errors[0]) + "\' in: " + str(used_mod[0]) +
                             "\nModule: " + str(used_mod[0]) + ", Error: " + str(item[0]) +
                             ", Near: " + str(item[1]) + ", Line: " + str(item[2] + "\n"))
                    sys.stderr.write(error)
