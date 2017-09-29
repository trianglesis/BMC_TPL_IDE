"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import itertools
import logging
import os
import re
import subprocess
import sys
import time

try:
    import progressbar
except ModuleNotFoundError:
    progressbar = False
    pass
except ImportError:
    progressbar = False
    pass

log = logging.getLogger("check.logger")


class SyntaxCheck:
    """
        1. Use working dir and tpl ver and run syntax check (input)
        2. Save syntax check result
        2.1 If pass - update var with syntax_passed = True
        2.2 If fail syntax_passed = Fail
        3. Return syntax check results

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

        bar     = ''
        spinner = ''
        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stdout()
            widgets = [progressbar.AnimatedMarker(),
                       ' Checking syntax. ',
                       progressbar.Timer()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          max_value=progressbar.UnknownLength,
                                          redirect_stdout=True)
        else:
            spinner = itertools.cycle(['-', '/', '|', '\\'])
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        tpl_mod_dir     = os.path.abspath(os.path.join(__file__ , "../.."))
        tplint_exe_path = tpl_mod_dir + '\\tplint\\tplint.exe'
        tplint_tax_path = tpl_mod_dir+'\\taxonomy\\00taxonomy.xml'
        syntax_passed   = False

        # errors_re = re.compile("\s+Errors:\s+(.+)")
        # mod_re = re.compile("Module:\s+(.+)")
        match_result = re.compile("(?P<error>\w+\s\w+) at or near '(?P<near>\S+)', "
                                  "line (?P<line>\d+), in (?P<module>\S+)")

        log.debug("Syntax: Will check all files in path: " + str(working_dir))

        if disco_ver not in self.SYNTAX_SUPPORTED:
            log.info("NOTE: tplint was updated in 2016 last time, "
                     "so we can use only version which is not greater then 11.0")
            disco_ver = 11.0

        # Lines will be collected in list:
        result_out = []
        if os.path.exists(tplint_exe_path) and os.path.exists(tplint_tax_path):
            cmd = " --discovery-versions="+str(disco_ver)+" --loglevel=WARN -t "+tplint_tax_path

            # noinspection PyBroadException
            try:
                open_path = subprocess.Popen(tplint_exe_path+cmd, cwd=working_dir, stdout=subprocess.PIPE)

                # Show progress with fancy progressbar:
                while open_path.stdout is not None:
                    if progressbar:
                        bar.update()
                    else:
                        sys.stdout.write(next(spinner))
                        sys.stdout.flush()
                        sys.stdout.write('\b')  # Working fine in win CMD but not in PyCharm.

                    out = open_path.stdout.readline()
                    result_out.append(out.decode('UTF-8').rstrip('\r'))

                    if not out:
                        break
                    time.sleep(0.01)
                # Final result:
                result = ''.join(result_out)
                if "No issues found!" in result:
                    # Close bar, do not forget to.
                    if progressbar:
                        bar.finish()
                    log.info("Build OK: Syntax: PASSED!")
                    syntax_passed = True

                elif match_result.findall(result):
                    # Close bar, do not forget to.
                    if progressbar:
                        bar.finish()
                    # error_modules = mod_re.findall(result)
                    # errors = errors_re.findall(result)
                    log.error("Syntax: ERROR: Some issues found!""\n" + str(result))
                else:
                    log.error("Syntax: Something is not OK \n" + str(result))
            except:
                log.error("Syntax: Tplint cannot run, check if working dir is present!")
                log.error("Syntax: Tplint use path: " + tpl_mod_dir)
        else:
            log.warning("Path to tplint module is not exist. Please check this: "
                        "https://github.com/trianglesis/BMC_TPL_IDE#syntax-check")
            # noinspection PyPep8
            log.debug("Those paths expected: "
                      "\ntplint_exe_path - "+str(tplint_exe_path) +
                      "\ntplint_tax_path - "+str(tplint_tax_path))

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
