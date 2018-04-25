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


log = logging.getLogger("check_ide.logger")


class AddmOperations:

    def __init__(self, ssh):
        """
        Class should be init with active SSH function.
        If no SSH - no work will done here.


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
        self.ssh_cons = ssh

        # noinspection SpellCheckingInspection
        self.upload_activated_check = re.compile('(\d+\sknowledge\supload\sactivated)')
        self.upload_num_item = re.compile('Uploaded\s+\S+\s+as\s\"([^"]+)\"')

    # noinspection PyBroadException
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
            raise FileNotFoundError

        if zip_on_local:
            self.file_check(zip_on_local, zip_on_remote)
        else:
            self.file_check(zip_on_remote, zip_on_local)

    # noinspection PyBroadException
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
         "\t\tSyntax error at or near 'check_ide' at line 15\n",
         'Pattern module BMC.RemedyARSystem\n',
         '\tWarnings:\n',
         '\t\tDeactivating BMC.RemedyARSystem to use newly activated module\n',
         '\n']


        :param system_password: str
        :param system_user: str
        :param zip_path: Path to zip with patterns uploaded or mirrored
        :param module_name: Name of pattern folder
        """
        result_out = []

        uploaded_activated = False  # 1 knowledge upload activated
        log.debug("Activate local zip: ensure we have rights of 777 on this file: "+str(zip_path))
        log.info("Installing and activating modules.")

        # Lines will be collected in list:
        tw_pattern_management = "/usr/tideway/bin/tw_pattern_management -u " + system_user + " -p " + system_password
        install_activ_progress = " --show-progress " + " --install-activate "+str(zip_path)

        try:
            self.ssh_cons.exec_command("chmod 777 "+str(zip_path))
            try:
                _, stdout, stderr = self.ssh_cons.exec_command(tw_pattern_management + install_activ_progress)
                # Show progress with fancy progressbar:
                msg = ' Activating knowledge update. '
                baring = self.progress_bar(msg)

                # Show progress with fancy progressbar:
                while stdout is not None:
                    if progressbar:
                        baring.update()
                    else:
                        sys.stdout.write(next(baring))
                        sys.stdout.flush()
                        sys.stdout.write('\b')  # Working fine in win CMD but not in PyCharm.

                    out = stdout.readlines()
                    raw_out = "".join(out)
                    result_out.append(raw_out.rstrip('\r'))
                    if not out:
                        break
                    time.sleep(0.1)

                # Final result:
                result = ''.join(result_out)
                if result:
                    item = self.upload_num_item.findall(result)
                    if self.upload_activated_check.findall(result):
                        if progressbar:
                            baring.finish()
                        uploaded_activated = True
                        log.info("Upload activating: " + "PASSED!")
                        log.info("Upload successfully. Module: " + str(module_name) +
                                 " as "+str(item[0]))
                    else:
                        if progressbar:
                            baring.finish()
                        log.critical("Pattern activation run with errors or warnings!")
                        log.critical("Detailed description from ADDM: \n"+result)
            except:
                raise Exception("Activation tw_pattern_management command cannot run!")
        except:
            raise Exception("Command 'chmod 777' cannot run on path: "+str(zip_path))

        return uploaded_activated

    def wipe_tku(self, system_user, system_password):
        """
        IDEA - run deactivate and removals if requested - before activate new.
        Clean patterns before upload new pack and run this only when arg flag is added.
        For example like: -wipe_tku = True.

        :return:
        """
        result_out = []

        log.debug("Func to deactivate previous or old TKU updates.")
        is_tkn_wiped = False
        log.info("CAUTION: Wiping all installed TKU in addm!")

        tw_pattern_management = "/usr/tideway/bin/tw_pattern_management -u " + system_user + " -p " + system_password
        remove_all_force = " --remove-all --force"

        try:
            _, stdout, stderr = self.ssh_cons.exec_command(tw_pattern_management + remove_all_force)

            # Show progress with fancy progressbar:
            msg = " Wiping all pattern modules. "
            baring = self.progress_bar(msg)

            # Show progress with fancy progressbar:
            while stdout is not None:
                if progressbar:
                    baring.update()
                else:
                    sys.stdout.write(next(baring))
                    sys.stdout.flush()
                    sys.stdout.write('\b')  # Working fine in win CMD but not in PyCharm.

                out = stdout.readlines()
                raw_out = "".join(out)
                result_out.append(raw_out.rstrip('\r'))
                if not out:
                    break
                time.sleep(0.1)

            # Final result:
            result = ''.join(result_out)
            if "Removed all pattern modules" in result:
                # Close bar, do not forget to.
                if progressbar:
                    baring.finish()
                is_tkn_wiped = True
                log.info("All TKU modules were wiped!")
            elif "No pattern modules to remove" in result:
                # Close bar, do not forget to.
                if progressbar:
                    baring.finish()
                is_tkn_wiped = True
                log.info("No pattern modules to remove.")
            else:
                # Close bar, do not forget to.
                if progressbar:
                    baring.finish()
                log.warning("Command 'tw_pattern_management --remove-all --force' cannot run:\n"+str(result))
        except:
            raise Exception("Wiping tw_pattern_management command cannot run!")

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

    # noinspection PyBroadException
    def tests_executor(self, tests_list, tst_cond):
        """
        This function execute tests for patterns.
        For test run - test list should be used, even with 1 element.

        Before run it will load bash_profile to activate paths to python, tideway, core etc.
        Progress will be shown if progressbar2 installed in local python libs.

        :param tst_cond:
        :param tests_list: list
        :return:
        """

        test_verbose_arg = ''
        test_failfast_arg = ''
        if tst_cond['test_verbose']:
            test_verbose_arg = ' --failfast'
        if tst_cond['test_failfast']:
            test_failfast_arg = ' --verbose'
        test_args = test_verbose_arg+test_failfast_arg

        if tests_list:
            log.info("-==== START TESTS EXECUTION ====-")
            tests_len = len(tests_list)
            log.info("Tests related to: "+str(tests_list[0]['pattern']))
            log.info("All tests len: "+str(tests_len))

            # Run test: 0 of 10 | - should be fixed, but I have no workaround.
            if progressbar:
                widgets = [
                           'Run test: ',
                           progressbar.SimpleProgress(), ' ',
                           progressbar.Percentage(), ' ',
                           progressbar.Bar('#'),
                           progressbar.Timer(), ' ',
                           progressbar.ETA(), ' ',
                           # ' Calculated ',
                           # progressbar.AdaptiveETA(), ' ',
                           progressbar.AbsoluteETA(),
                           '.\n']
                bar = progressbar.ProgressBar(widgets=widgets,
                                              max_value=tests_len,
                                              redirect_stdout=True,
                                              redirect_stderr=True)
            else:
                log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
                pass

            # TODO: log.debug("Run test for: PLACE HERE NAME OF FOLDER WE TESTING NOW.")
            for i, test in enumerate(tests_list):
                """
                export TKN_MAIN=/usr/tideway/TKU/addm/tkn_main/
                export TKN_CORE=$TKN_MAIN/tku_patterns/CORE
                export PYTHONPATH=$PYTHONPATH:$TKN_MAIN/python
                """
                i = i + 1
                log.info("Start test: " + str(test['rem_test_path'])+test_args)

                pre_cmd = ". ~/.bash_profile;"

                wd_cmd = "cd "+test['rem_test_wd']+";"

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
                        sys.stdout.write('\b')
                        log.debug("\n"+raw_out)
                    # This pipe of for unittest output only:
                    if stderr:
                        output = stderr.readlines()
                        raw_out = "".join(output)
                        sys.stdout.write('\b')
                        log.info("-==== UNITTEST LOG ====-")
                        log.info("\n\n"+raw_out)
                except:
                    # Not raise - see what happen with others:
                    log.error("Test execution command cannot run: "+str(cmd))
            if progressbar:
                bar.finish()  # Close bar, do not forget to.
            log.info("-==== END OF TESTS EXECUTION ====-")

        else:
            log.warning("There are no related tests found for current pattern!")

    @staticmethod
    def progress_bar(msg):
        """
        Show progress.
        Input message string.
        Output bar or spinner.

        :param msg:
        :return:
        """
        # progressbar = False
        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stdout()
            widgets = [progressbar.AnimatedMarker(),
                       msg,
                       progressbar.Timer()]
            bar = progressbar.ProgressBar(widgets=widgets,
                                          max_value=progressbar.UnknownLength,
                                          redirect_stdout=True,
                                          redirect_stderr=True)
            return bar

        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            spinner = itertools.cycle(['-', '/', '|', '\\'])
            return spinner

    def file_check(self, zip_on_local, zip_on_remote):
        """
        Run MD5 sum check_ide function. Raise error when sum not equal.

        :return:
        """
        file_check = self.check_file_pattern(local_file=zip_on_local, remote_file=zip_on_remote)
        if file_check:
            log.debug("File was found on ADDM file system.")
        else:
            log.error("File was found or not uploaded on ADDM file system.")
            raise FileNotFoundError
