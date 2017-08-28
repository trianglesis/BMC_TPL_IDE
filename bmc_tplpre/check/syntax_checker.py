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

    def __init__(self, logging):
        """

        :param logging: log class
        """

        self.logging = logging

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
        log = self.logging
        tpl_mod_dir = os.getcwd()
        syntax_passed = False

        errors_re = re.compile("\s+Errors:\s+(.+)")
        mod_re = re.compile("Module:\s+(.+)")

        match_result = re.compile("(?P<error>\w+\s\w+) at or near '(?P<near>\S+)', "
                                  "line (?P<line>\d+), in (?P<module>\S+)")

        log.debug("Syntax: Will check all files in path: " + str(working_dir))

        if disco_ver not in self.SYNTAX_SUPPORTED:
            log.info("NOTE: tplint was updated in 2016 last time, "
                     "so we can use only version which is not greater then 11.0")
            disco_ver = 11.0

        try:
            log.debug("Syntax: Checking syntax. Options: --discovery-versions="+str(disco_ver) +
                      " --loglevel=WARN"+" -t "+tpl_mod_dir+" in: "+str(working_dir))

            open_path = subprocess.Popen('"' + tpl_mod_dir + '\\tplint\\tplint.exe"'
                                                             ' --discovery-versions='+str(disco_ver) +
                                                             ' --loglevel=WARN'
                                                             ' -t "'+tpl_mod_dir+'\\taxonomy\\00taxonomy.xml"',
                                         cwd=working_dir, stdout=subprocess.PIPE)
            result = open_path.stdout.read().decode()
            if "No issues found!" in result:
                syntax_passed = True
                log.info("Syntax: PASSED!")
            elif match_result.findall(result):
                # error_modules = mod_re.findall(result)
                # errors = errors_re.findall(result)
                log.error("Syntax: ERROR: Some issues found!""\n" + str(result))
            else:
                log.debug("Syntax: Something is not OK \n" + str(result))

        except:
            log.error("Syntax: Tplint cannot run, check if working dir is present!")
            log.error("Syntax: Tplint use path: " + tpl_mod_dir)

        return syntax_passed

    @staticmethod
    def parse_syntax_result(result):
        """
        This will output errors in STDERR for tplint only.

        :param result:
        :return:
        """
        # log = self.logging
        match_result = re.compile("(?P<error>\w+\s\w+) at or near"
                                  " '(?P<near>\S+)', line (?P<line>\d+), in (?P<module>\S+)")
        used_mod_re = re.compile("Module:\s(\S+)\s\s+Errors:")
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
