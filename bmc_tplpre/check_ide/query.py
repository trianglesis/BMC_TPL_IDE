"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""
import logging
log = logging.getLogger("check_ide.logger")

"""
Query discovered results.
Save models
Etc.

"""

'''

usage: tw_query [options] query

where options can be

      --csv                   Output CSV
      --delimiter=CHAR        Delimiter character used in CSV files
      --file=FILE             Output CSV file
      --filedump              Dump to files specified in first column
  -h, --help                  Display help on standard options
      --loglevel=LEVEL        Logging level: debug, info, warning, error, crit
      --model-loglevel=LEVEL  Model log level
      --no-headings           Plain output with no headings
  -p, --password=PASSWD       Password
      --passwordfile=PWDFILE  Pathname for Password File
      --time                  Time queries
  -u, --username=NAME         Username
  -v, --version               Display version information
      --xml                   Output XML

and where query is the query to send to the Search service


'''