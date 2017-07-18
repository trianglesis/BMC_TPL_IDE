import subprocess
import re
import sys

'''
1. Use working dir and tpl ver and run syntax check (input)
2. Save syntax check result
2.1 If pass - update var with syntax_passed = True
2.2 If fail syntax_passed = Fail
3. Return syntax check results and details (output)
'''


def syntax_check(curr_work_dir, working_dir, tpl_version):
    """
    Check the syntax in working dir for all found files.

    :param curr_work_dir:
    :param working_dir:
    :param tpl_version:
    :return:
    """
    errors_re = re.compile("\s+Errors:\s+(.+)")
    mod_re = re.compile("Module:\s+(.+)")
    match_result = re.compile("(?P<error>\w+\s\w+) at or near '(?P<near>\S+)', line (?P<line>\d+), in (?P<module>\S+)")

    result = ''
    syntax_passed = False
    messages = [{"log": "debug", "msg": "DEBUG: Will check all files in path: " + " " * 27 + str(working_dir)}]

    # print('"' + curr_work_dir + '\\tplint\\tplint.exe" --discovery-versions=' + tpl_version + ' --loglevel=WARN -t "'+ curr_work_dir + '\\taxonomy\\00taxonomy.xml"')
    # print("WORK DIR CWD: "+str(working_dir))
    try:
        open_path = subprocess.Popen('"' + curr_work_dir + '\\tplint\\tplint.exe" --discovery-versions=' + tpl_version +
                                     ' --loglevel=WARN -t "'+ curr_work_dir + '\\taxonomy\\00taxonomy.xml"',
                                     cwd=working_dir, stdout=subprocess.PIPE)
        result = open_path.stdout.read().decode()
        if "No issues found!" in result:
            syntax_passed = True
            messages.append({"log": "info", "msg": "INFO: Syntax:" + " " * 51 + "PASSED!"})
        elif match_result.findall(result):
            error_modules = mod_re.findall(result)
            errors = errors_re.findall(result)
            messages.append({"log": "error", "msg": "ERROR: Some issues found!"
                                                    "\n" + "Module " + str(error_modules) + "\nErrors: " + str(errors)})
        else:
            print("Something is not OK: ")
            print(result)
    except:
        messages.append({"log": "error", "msg": "ERROR: Tplint cannot run, check if working dir is present!"})
        messages.append({"log": "error", "msg": "ERROR: Tplint use path:" + " " * 5 + curr_work_dir})

    return syntax_passed, messages, result


def parse_syntax_result(result):
    """
    This will output errors in STDERR for tplint only.

    :param result:
    :return:
    """
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
