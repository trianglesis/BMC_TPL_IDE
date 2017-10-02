"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import logging
log = logging.getLogger("check_ide.logger")

"""
Collecting data after Discovery run
- or after query success
- or each scan
- or optionally

[tideway@localhost sbin]$ tw_dml_extract -p system -h
usage: tw_dml_extract [options] query

where options can be

      --dip-support           Generate DIP support file
  -h, --help                  Display help on standard options
      --loglevel=LEVEL        Logging level: debug, info, warning, error, crit
      --lookup=ARG            Node ID to lookup (search ignored)
  -o, --output=ARG            Output file/prefix (ignored with -N)
  -p, --password=PASSWD       Password
      --passwordfile=PWDFILE  Pathname for Password File
  -S, --split                 Split output
  -N, --use-name              Use node name as filename when splitting
  -u, --username=NAME         Username
  -v, --version               Display version information

and where query is the search query to run

"""