"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""
import logging
log = logging.getLogger("check.logger")

class AddmScan:

    def __init__(self, ssh):
        """
        1. If pattern module uploaded successfully and activated - start this (input)
        1.1 Open saved SSH session if exist. (input)
        2. Check or change tw_disco_control (standard|playback|record)
        3. Check or start tw_scan_control --start
        4. Start scan with passed arguments: pattern_name, host_list
        5. Show result, scan ID ect. (output)

        :param ssh: func
        """

        self.ssh_cons = ssh

    def addm_scan(self, disco_mode, host_list, system_user, system_password, dir_label):
        """
        Start scan with hosts from args.

            usage: tw_scan_control [options] args

            where options can be

              -a, --add                   Add a new scan range
                  --allow-tpl-scan        Allow patterns to start new scan against these IPs
                  --clean                 Synonym for --clear (Obsolete)
                  --clear                 Remove all scan ranges
                  --company=NAME          Multi-tenant Company for scan
                  --daily                 Daily scheduled scan
                  --disable               Disable chosen scheduled scans
                  --duration=DD:HH:MM     Duration of scheduled scan
                  --enable                Disable chosen scheduled scans
                  --end-time=HH:MM        End time of scheduled scan
              -f, --file                  Expect a list of files as arguments
              -h, --help                  Display help on standard options
                  --label=LABEL           Label for scan
                  --list                  List all scan ranges
                  --list-full             List all scan ranges with all IP addresses
                  --loglevel=LEVEL        Logging level: debug, info, warning, error, crit
                  --monthly               Monthly scheduled scan
                  --monthly-end-day=DAY   Monthly scheduled scan end day (1-31)
                  --monthly-start-day=DAY Monthly scheduled scan start day (1-31)
                  --monthly-start-week=WEEK
                                          Monthly scheduled scan start week (first, .., fourth, last)
                  --monthly-start-week-day=WEEKDAY
                                          Monthly scheduled scan start week day of week (monday, tuesday, etc)
                  --no-end-time           Scheduled scan runs to completion
                  --passphrase=ARG        Vault passphrase
              -p, --password=PASSWD       Password
                  --passwordfile=PWDFILE  Pathname for Password File
              -r, --random                Randomly shuffle IP list
                  --recur-daily           Add a daily recurrent range
                  --recurrence-duration=DURATION
                                          Duration for recurrent range (hours)
                  --recurrence-start=HOUR Start time for recurrent range
                  --remove                Remove chosen scan ranges
                  --replace=ID            Synonym for --update (Obsolete)
              -l, --scan-level=LEVEL      Scan level to use
                  --scanLevel=LEVEL       Scan level to use (Obsolete)
                  --silent                Turn off informational messages
              -s, --start                 Start reasoning
                  --start-time=HH:MM      Start time of scheduled scan
              -x, --stop                  Stop reasoning
                  --update=ID             Update existing scheduled scan
              -u, --username=NAME         Username
              -v, --version               Display version information
                  --weekly                Weekly scheduled scan
                  --weekly-end-week-day=WEEKDAY
                                          Weekly scheduled scan end week day (monday, tuesday, etc)
                  --weekly-start-week-days=WEEKDAYS
                                          Weekly scheduled scan list of start week days (monday, tuesday, etc)

            and where args is
            * with --disable, --enable or --remove, a list of range IDs
            * with -f a list of filenames containing IP ranges to scan
            * otherwise a list of IP ranges to scan


        :param system_password: str
        :param system_user: str
        :param disco_mode: str - discovery mode
        :param host_list: list - list of hosts to scan. Now only ipv4 supported.
        :param dir_label: Name of folder where pattern executed.
        """

        if disco_mode:
            stdin, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_disco_control"
                                                               " -u " + system_user +
                                                               " -p " + system_password +
                                                               " --"+disco_mode)
        else:
            stdin, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_disco_control"
                                                               " -u " + system_user +
                                                               " -p " + system_password +
                                                               " --standard")

        if stdout:
            result = stdout.readlines()
            log.debug("Discovery mode is: " + result[0]+" Discovery status:" + result[1])
            log.info("Discovery started")

        log.info("Host(s) to scan: " + host_list)
        log.info("Scan named as: " + dir_label)

        self.ssh_cons.exec_command("/usr/tideway/bin/tw_scan_control"
                                   " -u " + system_user +
                                   " -p " + system_password +
                                   " --start")
        stdin, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_scan_control"
                                                           " -u " + system_user +
                                                           " -p " + system_password +
                                                           " --add"
                                                           " --label="+dir_label+""
                                                           " --loglevel=debug"
                                                           " --list "+host_list)
        if stdout:
            result = stdout.read().decode()
            if result:
                log.info("Scan been added:\n"+result)
        if stderr:
            result = stdout.read().decode()
            if result:
                log.error("Scan has not been added:\n"+result)

    def addm_scan_check(self, ssh, scan_id):
        """
        Check scan status.
        Return when scan is finished.

        :param ssh:
        :param scan_id:
        :return:
        """
        if ssh:
            log.debug('addm_scan_check')
            if scan_id:
                log.debug('scan_id')

    def addm_scan_reasoning_on_off(self, ssh, reasoning_flag):
        """
        Start/Stop reasoning.


        :param ssh: func
        :param reasoning_flag: str
        :return:
        """
        if ssh:
            log.debug('addm_scan_reasoning_on_off')
            if reasoning_flag:
                log.debug('reasoning_flag')
