"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import hashlib
import re


class AddmOperations:

    def __init__(self, logging, ssh):
        """

        1. If syntax_passed = True AND tpl_preproc = True AND addm_host ip in args - start this (input)
        2. If there is no pattern file situated BUT working dir - make zip of dir content *.tpl
            with correspond tpl ver from Tplpreproc folders
        3. Open SSH session \ Save opened

        IF not 'dev_vm_check': True:
            Programm will try to upload package via SFTP

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

        :param logging: func
        :param ssh: func
        """
        # TODO: Plan to upload other files (or use as DEV VM) - dml, py, etc.

        self.logging = logging
        self.ssh_cons = ssh

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

        log = self.logging

        log.info("zip file local: " + zip_on_local)
        log.info("zip file remote: " + zip_on_remote)

        ftp = self.ssh_cons.open_sftp()
        try:
            ftp.put(zip_on_local, zip_on_remote)
            ftp.close()
            log.info("Patterns zip to ADDM upload:" + "PASSED!")
        except:
            log.error("Something goes wrong with ftp connection or zip file! Check if file path or folder exists")

        if zip_on_local:
            file_check = self.check_file_pattern(local_file=zip_on_local, remote_file=zip_on_remote)
        else:
            file_check = self.check_file_pattern(local_file=zip_on_remote, remote_file=zip_on_local)

        return file_check

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

        log = self.logging

        uploaded_activated = False  # 1 knowledge upload activated
        log.debug("Activate local zip: ensure we have rights of 777 on this file: "+str(zip_path))

        self.ssh_cons.exec_command("chmod 777 "+str(zip_path))
        log.info("Installing and activating pattern modules.")

        _, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_pattern_management"
                                                       " -u " + system_user +
                                                       " -p " + system_password +
                                                       " --install-activate "+str(zip_path))

        # TODO: Is there a way to draw a progress bar until it activating?
        if stdout:
            output = stdout.readlines()
            raw_out = "".join(output)
            item = self.upload_num_item.findall(raw_out)
            if self.upload_activated_check.findall(raw_out):
                uploaded_activated = True
                log.info("Upload activating: " + "PASSED!")
                log.info("Pattern uploaded successfully. Module: " + str(module_name)+" as "+str(item[0]))
            else:
                log.critical("Pattern activation failed! Scan will not start.")
                log.critical("Detailed description from ADDM: \n"+raw_out)

        return uploaded_activated

    def deactivate_tku(self):
        """
        IDEA - run deactivate and removals if requested - before activate new.

        :return:
        """
        log = self.logging

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
        log = self.logging

        log.debug("MD5SUM: Checking file sum of local_file: "+str(local_file))
        log.debug("MD5SUM: Checking file sum of remote_file: "+str(remote_file))

        local_hash5 = hashlib.md5(open(local_file, 'rb').read()).hexdigest()
        _, stdout, stderr = self.ssh_cons.exec_command("md5sum " + remote_file)
        output_ok = stdout.readlines()

        if local_hash5 in output_ok[0]:
            log.debug("Checksum of files is OK!\n Local sum:  " + local_hash5 + "\n Remote sum: " + output_ok[0])
            file_ok = True
        else:
            log.debug("Checksum of files is DIFFERENT!\n Local sum: " + local_hash5 + "\n Remote sum: " + output_ok[0])
            file_ok = False

        return file_ok

