"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import itertools
import hashlib
import re
import logging
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


class AddmOperations:

    def __init__(self, ssh):
        """

        1. If syntax_passed = True AND tpl_preproc = True AND addm_host ip in args - start this (input)
        2. If there is no pattern file situated BUT working dir - make zip of dir content *.tpl
            with correspond tpl ver from Tplpreproc folders
        3. Open SSH session \ Save opened

        IF not 'dev_vm_check': True:
            Program will try to upload package via SFTP

            3.1 Check upload folder \ Create if no folder found \ Wipe if any old file found
            3.2 Check pattern or zip in filesystem AND start upload to ADDM
            3.1 Check upload completed (pattern or zip) and run --install-activate

        IF 'dev_vm_check': True:
            Nothing will be uploaded via SFTP because there is a local share found.

            3.1 Compose path from local pattern to same remote in dev.
            3.1 Execute ssh command with path as remote share to pattern package and activate

        Idea:
            3.1.1 Try to deactivate unused modules - IDEA

        4 When activate finished - return result (pass \ fail) - (output)

        :param ssh: func
        """
        # TODO: Plan to upload other files (or use as DEV VM) - dml, py, etc.
        self.ssh_cons = ssh

        # noinspection SpellCheckingInspection
        self.upload_activated_check = re.compile('(\d+\sknowledge\supload\sactivated)')
        self.upload_num_item = re.compile('Uploaded\s+\S+\s+as\s\"([^"]+)\"')

    def upload_knowledge(self, zip_on_local, zip_on_remote):
        """
        Use local path to zip file and remote path where to download.
        Check md5sum of both files after upload.
        Use hardcoded path.
            This path should be checked and created in parse_args.check_folders()

        :param zip_on_local: str - path to zip in local system
        :param zip_on_remote: str - path where put this zip
        """

        log.debug("zip file local: " + zip_on_local)
        log.debug("zip file remote: " + zip_on_remote)

        sftp = self.ssh_cons.open_sftp()
        try:
            sftp.put(zip_on_local, zip_on_remote)
            sftp.close()
            log.info("Patterns upload:" + "PASSED!")
        except:
            log.error("Something goes wrong with sftp connection or zip file! Check if file path or folder exists")

        if zip_on_local:
            file_check = self.check_file_pattern(local_file=zip_on_local, remote_file=zip_on_remote)
            if file_check:
                log.debug("File was found on ADDM file system.")
            else:
                log.error("File was found or not uploaded on ADDM file system.")
                raise FileNotFoundError
        else:
            file_check = self.check_file_pattern(local_file=zip_on_remote, remote_file=zip_on_local)
            if file_check:
                log.debug("File was found on ADDM file system.")
            else:
                log.error("File was found or not uploaded on ADDM file system.")
                raise FileNotFoundError

        # return file_check

    def activate_knowledge(self, zip_path, module_name, system_user, system_password):
        """
        Give it path where zip folder can be:
            - for dev_vm - mirror FS
            - for usual - SFTP path

        Nothing to delete REMOTELY.
        Wipe only old zip LOCALLY!

        ['Uploaded /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/
                    PatternFolder/imports/tpl113/PatternFile.zip as "PatternFile upload 10"\n',
         'Failed to activate 1 knowledge upload\n',
         'Pattern module BMC.RemedyARSystem\n',
         '\tErrors:\n',
         "\t\tSyntax error at or near 'check' at line 15\n",
         'Pattern module BMC.RemedyARSystem\n',
         '\tWarnings:\n',
         '\t\tDeactivating BMC.RemedyARSystem to use newly activated module\n',
         '\n']


        :param system_password: str
        :param system_user: str
        :param zip_path: Path to zip with patterns uploaded or mirrored
        :param module_name: Name of pattern folder
        """

        # progressbar = False
        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stdout()
            widgets = [progressbar.AnimatedMarker(),
                       ' Activating knowledge update. ',
                       progressbar.Timer()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          max_value=progressbar.UnknownLength,
                                          redirect_stdout=True,
                                          redirect_stderr=True)
        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        uploaded_activated = False  # 1 knowledge upload activated
        log.debug("Activate local zip: ensure we have rights of 777 on this file: "+str(zip_path))
        log.info("Installing and activating modules.")

        # Lines will be collected in list:
        result_out = []
        spinner = itertools.cycle(['-', '/', '|', '\\'])

        try:
            self.ssh_cons.exec_command("chmod 777 "+str(zip_path))
            try:
                _, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_pattern_management"
                                                               " -u " + system_user +
                                                               " -p " + system_password +
                                                               " --show-progress " +
                                                               " --install-activate "+str(zip_path))
                # Show progress with fancy progressbar:
                if progressbar:
                    while stdout is not None:
                        bar.update()
                        out = stdout.readlines()
                        raw_out = "".join(out)
                        result_out.append(raw_out.rstrip('\r'))
                        if not out:
                            break
                        time.sleep(0.1)
                # There is no progressbar - show just simple spinner:
                else:
                    while stdout is not None:
                        sys.stdout.write(next(spinner))
                        sys.stdout.flush()
                        sys.stdout.write('\b')  # Working fine in win CMD but not in PyCharm.

                        out = stdout.readlines()
                        raw_out = "".join(out)
                        result_out.append(raw_out.rstrip('\r'))

                        if not out:
                            sys.stdout.flush()  # Remove spinner from output.
                            break
                        time.sleep(0.1)
                # Final result:
                result = ''.join(result_out)
                if result:
                    item = self.upload_num_item.findall(result)
                    if self.upload_activated_check.findall(result):
                        if progressbar:
                            bar.finish()
                        uploaded_activated = True
                        log.info("Upload activating: " + "PASSED!")
                        log.info("Upload successfully. Module: " + str(module_name)+
                                 " as "+str(item[0]))
                    else:
                        if progressbar:
                            bar.finish()
                        log.critical("Pattern activation run with errors or warnings!")
                        log.critical("Detailed description from ADDM: \n"+result)
            except:
                log.warning("Activation tw_pattern_management command cannot run!")
        except:
            log.warning("Command 'chmod 777' cannot run on path: "+str(zip_path))

        return uploaded_activated

    def wipe_tku(self, system_user, system_password):
        """
        IDEA - run deactivate and removals if requested - before activate new.
        Clean patterns before upload new pack and run this only when arg flag is added.
        For example like: -wipe_tku = True.

        :return:
        """

        # progressbar = False
        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stdout()
            widgets = [progressbar.AnimatedMarker(),
                       ' Wiping TKU. ',
                       progressbar.Timer()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          max_value=progressbar.UnknownLength,
                                          redirect_stdout=True,
                                          redirect_stderr=True)
        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        log.debug("Func to deactivate previous or old TKU updates.")
        is_tkn_wiped = False
        log.info("CAUTION: Wiping all installed TKU in addm!")

        # Lines will be collected in list:
        result_out = []
        spinner = itertools.cycle(['-', '/', '|', '\\'])

        try:
            _, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_pattern_management"
                                                           " -u " + system_user +
                                                           " -p " + system_password +
                                                           " --remove-all --force")
            # Show progress with fancy progressbar:
            if progressbar:
                while stdout is not None:
                    bar.update()
                    out = stdout.readlines()
                    raw_out = "".join(out)
                    result_out.append(raw_out.rstrip('\r'))
                    if not out:
                        break
                    time.sleep(0.1)
            # There is no progressbar - show just simple spinner:
            else:
                while stdout is not None:
                    sys.stdout.write(next(spinner))
                    sys.stdout.flush()
                    sys.stdout.write('\b')  # Working fine in win CMD but not in PyCharm.

                    out = stdout.readlines()
                    raw_out = "".join(out)
                    result_out.append(raw_out.rstrip('\r'))
                    if not out:
                        sys.stdout.flush()  # Remove spinner from output.
                        break
                    time.sleep(0.1)
            # Final result:
            result = ''.join(result_out)
            if "Removed all pattern modules" in result:
                # Close bar, do not forget to.
                if progressbar:
                    bar.finish()
                is_tkn_wiped = True
                log.info("All TKU modules were wiped!")
            else:
                # Close bar, do not forget to.
                if progressbar:
                    bar.finish()
                log.warning("Command 'tw_pattern_management --remove-all --force' cannot run:\n"+str(result))
        except:
            log.warning("Wiping tw_pattern_management command cannot run!")

        return is_tkn_wiped

    def check_file_pattern(self, local_file, remote_file):
        """
        Check the file sum to ensure it was downloaded successfully.

        Pattern:
        output_ok = ['be890ee8bee5f136ca10c03095e8ad60  /usr/tideway/TKU/Tpl_DEV/PatternFile.tpl\n']
        local_hash5 = be890ee8bee5f136ca10c03095e8ad60

        zip:
        output_ok = ['cc625d0ae7ea33885b6c1e7f67bcbf84  /usr/tideway/TKU/Tpl_DEV/PatternFile.zip\n']
        local_hash5 = cc625d0ae7ea33885b6c1e7f67bcbf84

        :param remote_file: file on ADDM
        :param local_file: file in local system
        :return:
        """

        local_hash5 = ''
        output_ok = ''

        log.debug("MD5SUM: Checking file sum of local_file: "+str(local_file))
        log.debug("MD5SUM: Checking file sum of remote_file: "+str(remote_file))

        try:
            local_hash5 = hashlib.md5(open(local_file, 'rb').read()).hexdigest()
            _, stdout, stderr = self.ssh_cons.exec_command("md5sum " + remote_file)
            output_ok = stdout.readlines()
            output_ok = output_ok[0]
        except FileNotFoundError as e:
            log.error("File cannot be found in this path. Message: "+str(e))

        if local_hash5 in output_ok:
            log.debug("Checksum of files is OK!\n Local sum:  " + local_hash5 + "\n Remote sum: " + output_ok)
            file_ok = True
        else:
            log.error("Checksum of files is DIFFERENT!\n Local sum: " + local_hash5 + "\n Remote sum: " + output_ok)
            file_ok = False

        return file_ok

    def tests_executor(self, tests_list, test_conditions):
        """
        Placeholder for tests run
        :param tests_list: list
        :return:
        """

        test_verbose_arg = ''
        test_failfast_arg = ''
        if test_conditions['test_verbose']:
            test_verbose_arg = ' --failfast'
        if test_conditions['test_failfast']:
            test_failfast_arg = ' --verbose'
        test_args = test_verbose_arg+test_failfast_arg

        tests_len = len(tests_list)

        # Run test: 0 of 10 | - should be fixed, but I have no workaround.
        if progressbar:
            widgets = [
                       'Run test: ',
                       progressbar.SimpleProgress(),
                       ' ', progressbar.Bar(),
                       ' ', progressbar.Timer(),
                       ' ', progressbar.Percentage(), ' ',
                       ' ', progressbar.ETA(),
                       ' Calculated ', progressbar.AdaptiveETA(),
                       ' ', progressbar.AbsoluteETA(),
                       '.'
                       ]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          max_value=tests_len,
                                          # redirect_stdout=True,
                                          redirect_stderr=True
                                          )
        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        log.info("-==== START RELATED TESTS EXECUTION ====-")
        log.debug("Run test for: PLACE HERE NAME OF FOLDER WE TESTING NOW.")
        log.info("Tests related to: "+str(tests_list[0]['pattern']))
        log.info("All tests len: "+str(tests_len))

        for i, test in enumerate(tests_list):
            """
            Remote run: 
            ssh://tideway@192.168.5.11:22/usr/bin/python -u /usr/tideway/TKU/addm/tkn_main/buildscripts/test_executor.py
            ssh://tideway@192.168.5.11:22/usr/tideway/bin/python -u /usr/tideway/TKU/addm/tkn_main/tku_patterns/CORE/MicrosoftAppFabric/tests/test.py TestStandalone.test2_Windows_main
            
            export TKN_MAIN=/usr/tideway/TKU/addm/tkn_main/
            export TKN_CORE=$TKN_MAIN/tku_patterns/CORE
            export PYTHONPATH=$PYTHONPATH:$TKN_MAIN/python

            # cmd = "cd "+test['rem_test_wd']+"; ls; python -u "+test['rem_test_path']+" --verbose"
            # cmd = "cd "+test['rem_test_wd']+"; /usr/tideway/bin/python --version"
            # cmd = "cd "+test['rem_test_wd']+"; python --version"
            # cmd = "cd "+test['rem_test_wd']+"; echo $TKN_MAIN"
            # cmd = "cd "+test['rem_test_wd']+"; echo $TKN_CORE"
            # cmd = "cd "+test['rem_test_wd']+"; echo $PYTHONPATH"
            # cmd = "cd "+test['rem_test_wd']+"; ls"

            Local run: ?
            """

            i = i + 1
            log.info("Start test: " + str(test['rem_test_path']))

            pre_cmd = ". ~/.bash_profile;"
            wd_cmd = "cd "+test['rem_test_wd']+";"
            # TODO: Add verbose and failfast as args:
            cmd_test = "/usr/tideway/bin/python -u "+test['rem_test_path']+test_args
            cmd = pre_cmd + wd_cmd + cmd_test
            log.debug("Run: "+str(cmd))

            # Show output and count of running tests and ETAs:
            if progressbar:
                bar(range(tests_len))
                bar.update(i)
            # Print simple counter:
            else:
                log.info("%d test of "+str(tests_len), i)

            try:
                _, stdout, stderr = self.ssh_cons.exec_command(cmd)
                # This pipe is for messages from test_utils and dml...
                if stdout:
                    output = stdout.readlines()
                    raw_out = "".join(output)
                    log.debug("-==== DETAILED LOG ====-")
                    log.debug("\n"+raw_out)
                # This pipe of for unittest output only:
                if stderr:
                    output = stderr.readlines()
                    raw_out = "".join(output)
                    log.info("-==== UNITTEST LOG ====-")
                    log.info("\n\n"+raw_out)
            except:
                log.error("Test execution command cannot run: "+str(cmd))
            # For debug:
            if i == 3:
                break
        # Close bar, do not forget to.
        if progressbar:
            bar.finish()
        log.info("-==== END OF RELATED TESTS EXECUTION ====-")