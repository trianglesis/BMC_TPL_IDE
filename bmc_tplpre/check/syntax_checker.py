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
3. Return syntax check results and details (output)
'''
# TODO: Make another syntax checking procedure maybe on python AST.


class SyntaxCheck:
    """
        Verify if tplint is present on current system.
        If not - use something another to check common errors and typos in tpl\tplpre files.
        to be continued...

        If tplpint is present - use arg from ask_addm to compare the version of tpl which addm support.
        Run check.
    """

    def __init__(self, logging):
        """

        :param logging: log class
        """

        self.logging = logging

    def syntax_check(self, working_dir):
        """
        Check the syntax in working dir for all found files.
        Tpl version for check will be used from ADDM.
        If no ADDM ip was added in args - will latest available hardcoded.

        Until tplint updated - it can check syntax only for max version 10.2.

        :param tpl_mod_dir: Place where tplint is situated. By default it should be place where TPL language module lies.
        :param working_dir:
        :return:
        """
        log = self.logging

        errors_re = re.compile("\s+Errors:\s+(.+)")
        mod_re = re.compile("Module:\s+(.+)")
        match_result = re.compile("(?P<error>\w+\s\w+) at or near '(?P<near>\S+)', line (?P<line>\d+), in (?P<module>\S+)")

        result = ''
        syntax_passed = False
        log.debug("Syntax: Will check all files in path: " + str(working_dir))

        tpl_mod_dir = os.getcwd()
        print(tpl_mod_dir)


        # NOTE: When checking syntax - is better to use all versions of tpl, because it can produce old-version errors.
        # It's longer but work for all versions.
        try:
            log.debug("Syntax: Checking syntax. Options: -a --loglevel=WARN"+" -t "+tpl_mod_dir+" in: "+str(working_dir))

            open_path = subprocess.Popen('"' + tpl_mod_dir + '\\tplint\\tplint.exe" '
                                                             '-a --loglevel=WARN -t "'
                                         + tpl_mod_dir + '\\taxonomy\\00taxonomy.xml"',
                                         cwd=working_dir, stdout=subprocess.PIPE)

            result = open_path.stdout.read().decode()

            if "No issues found!" in result:
                syntax_passed = True
                log.info("Syntax: PASSED!")

            elif match_result.findall(result):
                error_modules = mod_re.findall(result)
                errors = errors_re.findall(result)
                log.error("Syntax: ERROR: Some issues found!""\n" + "Module " + str(error_modules) + "\nErrors: " + str(errors))

            else:
                log.error("Syntax: Something is not OK. RAW Result:")
                log.error(result)
                log.debug("Syntax: Something is not OK \n" + str(result))

        except:
            log.error("Syntax: Tplint cannot run, check if working dir is present!")
            log.error("Syntax: Tplint use path: " +tpl_mod_dir)

        return syntax_passed, result

    def parse_syntax_result(self, result):
        """
        This will output errors in STDERR for tplint only.

        :param result:
        :return:
        """
        log = self.logging
        match_result = re.compile("(?P<error>\w+\s\w+) at or near '(?P<near>\S+)', line (?P<line>\d+), in (?P<module>\S+)")
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
