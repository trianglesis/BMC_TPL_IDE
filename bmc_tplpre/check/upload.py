"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import hashlib
import re
import logging
# import time

try:
    import progressbar
except ModuleNotFoundError:
    progressbar = ''
    pass
except ImportError:
    progressbar = ''
    pass

log = logging.getLogger("check.logger")

# TODO: Add one progressbar for all processes and call.
# if progressbar:
#     progressbar.streams.flush()
#     progressbar.streams.wrap_stderr()
#     bar = progressbar.ProgressBar(max_value=100)
# else:
#     log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
#     pass
# def progressbar(bar, len, i):
#     bar(range(len))
#     bar.update(i)


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
        # TODO: Check if exist or MD5 sum will do it better?

        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stderr()
            bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        uploaded_activated = False  # 1 knowledge upload activated
        log.debug("Activate local zip: ensure we have rights of 777 on this file: "+str(zip_path))

        log.info("Installing and activating modules.")

        try:
            self.ssh_cons.exec_command("chmod 777 "+str(zip_path))
            try:
                _, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_pattern_management"
                                                               " -u " + system_user +
                                                               " -p " + system_password +
                                                               " --install-activate "+str(zip_path))
                # while not stdout:
                #     time.sleep(0.001)
                #     for i in range(10):
                #         bar.update(i)
                #         log.debug("")

                if stdout:
                    output = stdout.readlines()
                    raw_out = "".join(output)
                    item = self.upload_num_item.findall(raw_out)
                    if self.upload_activated_check.findall(raw_out):
                        uploaded_activated = True
                        log.info("Upload activating: " + "PASSED!")
                        log.info("Upload successfully. Module: " + str(module_name)+" as "+str(item[0]))
                    else:
                        log.critical("Pattern activation run with errors or warnings!")
                        log.critical("Detailed description from ADDM: \n"+raw_out)
            except:
                log.warning("Activation tw_pattern_management command cannot run!")
        except:
            log.warning("Command 'chmod 777' cannot run on path: "+str(zip_path))

        # bar.finish()

        return uploaded_activated

    @staticmethod
    def deactivate_tku():
        """
        IDEA - run deactivate and removals if requested - before activate new.

        :return:
        """

        log.debug("Func to deactivate previous or old TKU updates.")

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

    def tests_executor(self, tests_list):
        """
        Placeholder for tests run
        :param tests_list: list
        :return:
        """
        tests_len = len(tests_list)

        if progressbar:
            progressbar.streams.flush()
            progressbar.streams.wrap_stderr()
            bar = progressbar.ProgressBar(max_value=tests_len)
        else:
            log.debug("Module progressbar2 is not installed, will show progress in usual manner.")
            pass

        log.info("-==== START RELATED TESTS EXECUTION ====-")
        log.debug("Run test for: PLACE HERE NAME OF FOLDER WE TESTING NOW.")
        log.debug("Tests related to: "+str(tests_list[0]['pattern']))
        log.debug("All tests len: "+str(tests_len))

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

            log.info("Start test:" + str(test['rem_test_path']))

            if progressbar:
                bar(range(tests_len))
                bar.update(i)
            else:
                pass

            log.info("%d test of "+str(tests_len), i+1)  # Just print

            pre_cmd = ". ~/.bash_profile;"
            wd_cmd = "cd "+test['rem_test_wd']+";"
            cmd_test = "/usr/tideway/bin/python -u "+test['rem_test_path']+" --verbose"

            cmd = pre_cmd + wd_cmd + cmd_test
            log.debug("Run: "+str(cmd))

            try:
                _, stdout, stderr = self.ssh_cons.exec_command(cmd)

                if stdout:
                    output = stdout.readlines()
                    raw_out = "".join(output)
                    log.info("-==== DETAILED LOG ====-")
                    log.info("\n"+raw_out)
                if stderr:
                    output = stderr.readlines()
                    raw_out = "".join(output)
                    log.info("-==== UNITTEST LOG ====-")
                    log.info("\n\n"+raw_out)
            except:
                log.error("Test execution command cannot run: "+str(cmd))
            # break

        if progressbar:
            bar.finish()
        else:
            pass
        log.info("-==== END OF RELATED TESTS EXECUTION ====-")