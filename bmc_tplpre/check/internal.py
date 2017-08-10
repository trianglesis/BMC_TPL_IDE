"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""



def local_syntax_check(full_path):
    """

    Found errors 'Syntax error' in: Apache.Oozie
    Module: Apache.Oozie, Error: Syntax error, Near: asasasdasdasdasdasd, Line: 11

    :param full_path:
    :return:
    """
    import sys

    print("Local check")
    print("Checking the pattern: "+str(full_path))
    output = ''
    messages = []

    messages.append({"log":"debug", "msg":"DEBUG: Importing patterns:"})

    # error = ("Found errors \'"+str(errors[0])+"\' in: "+str(used_mod[0])+"\nModule: "+str(used_mod[0])+", Error: "+str(item[0])+", Near: "+str(item[1])+", Line: "+str(item[2]+"\n"))

    error = ("Found errors \'Syntax error!\' in: "+str(full_path)+"\nModule: Apache.Oozie, Error: Syntax error, Near: asasasdasdasdasdasd, Line: 11\n")
    sys.stderr.write(error)

    return output, messages