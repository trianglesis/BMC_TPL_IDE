
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
      --loglevel=LEVEL        Logging level: debug, info, warn, error, crit
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