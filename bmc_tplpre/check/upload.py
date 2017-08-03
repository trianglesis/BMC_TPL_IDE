import hashlib
import os
import re
import zipfile


'''
1. If syntax_passed = True AND tpl_preproc = True AND addm_host ip in args - start this (input)
2. If there is no pattern file situated BUT working dir - make zip of dir content *.tpl
with correspond tpl ver from Tplpreproc folders
3. Open SSH session \ Save opened
3.1 Check upload folder \ Create if no folder found \ Wipe if any old file found
3.2 Check pattern or zip in filesystem AND start upload to ADDM
3.1 Check upload completed (pattern or zip) and run --install-activate

3.1.1 Try to deactivate unused modules - IDEA

4 When activate finished - return result (pass \ fail) - (output)

'''


class AddmOperations:

    def __init__(self, logging, ssh):

        self.logging = logging
        self.ssh_cons = ssh

    def upload_knowledge(self, pattern_name, dir_label, file_path):
        """
        In file_path: will be path to pattern file or folder (zip_path) on local filesystem to upload to ADDM


        1. Delete old content from Tpl_DEV folder.
        2. Upload file from local path to remote via sftp:
            - If pattern_name - then upload pattern file.
            - If no pattern_name - then, probably folder content should be uploaded. Make zip from folder content.
        3. If file path not null or false - check md5 sum of local file VS remote uploaded file.
            If sum equal - upload was finished successfully.

        4. Run pattern activation process. Check output, if knowledge activated - then upload and activation pass, if no
        output ssh console result with error or warning.


        usage: tw_pattern_management [options] <upload/[upload:]module/file>

        where options can be

              --activate-all          Activate all pattern modules
              --activate-module       Activate pattern module
              --activate-upload       Activate knowledge upload
              --deactivate-module     Deactivate pattern module
              --deactivate-upload     Deactivate knowledge upload
          -f, --force                 Deactivate patterns before removal
          -h, --help                  Display help on standard options
              --install               Install (but not activate) knowledge upload
              --install-activate      Install and activate knowledge upload
          -l, --list-uploads          List knowledge uploads
              --loglevel=LEVEL        Logging level: debug, info, warn, error, crit
          -p, --password=PASSWD       Password
              --passwordfile=PWDFILE  Pathname for Password File
              --remove-all            Remove all pattern modules
              --remove-module         Remove pattern module
              --remove-upload         Remove knowledge upload
              --show-progress         Write progress
          -u, --username=NAME         Username
          -v, --version               Display version information

        and where <upload/[upload:]module/file> is a knowledge upload name, pattern module identifier or existing file


        :param pattern_name: str
        :param dir_label: str
        :param file_path: str
        """

        log = self.logging

        output = ''
        zip_path = ''
        upload_activated_check = re.compile('\d+\sknowledge\supload\sactivated')

        # Wipe previous tpl dev uploads
        _, stdout, stderr = self.ssh_cons.exec_command("rm -rf /usr/tideway/TKU/Tpl_DEV/*")
        # Start FTP session with ADDM machine:
        if pattern_name:
            module_name = pattern_name
            log.info("Upload pattern to ADDM folder:" + "/usr/tideway/TKU/Tpl_DEV/")
            localpath = '/usr/tideway/TKU/Tpl_DEV/' + module_name + '.tpl'
            ftp = self.ssh_cons.open_sftp()
            try:
                ftp.put(file_path, localpath)
                ftp.close()
            except:
                log.error("Something goes wrong with ftp connection or zip file! Check if file path or folder exists")
        else:
            log.info("Making zip of all .tpl in folder:"  + file_path)
            log.info("Upload zip to ADDM folder:" + "/usr/tideway/TKU/Tpl_DEV/")

            module_name = dir_label
            zip_filename = module_name + '.zip'
            zip_path = file_path + zip_filename
            patterns_zip = zipfile.ZipFile(zip_path, 'w')
            log.debug("zip_filename:" + zip_filename)

            for foldername, subfolders, filenames in os.walk(file_path):
                for filename in filenames:
                    if filename != zip_filename:
                        patterns_zip.write(os.path.join(file_path, filename), arcname=filename)
                        log.debug("Adding pattern:" + filename)
            patterns_zip.close()

            log.info("zip_path:" + zip_path)
            localpath = '/usr/tideway/TKU/Tpl_DEV/' + zip_filename
            ftp = self.ssh_cons.open_sftp()
            try:
                ftp.put(zip_path, localpath)
                ftp.close()
                log.info("Patterns zip to ADDM upload:" + "PASSED!")
            except:
                log.error("Something goes wrong with ftp connection or zip file! Check if file path or folder exists")

        if zip_path:
            file_check = self.check_file_pattern(local_file=zip_path, remote_file=localpath)
        else:
            file_check = self.check_file_pattern(local_file=file_path, remote_file=localpath)

        uploaded_activated = False  # 1 knowledge upload activated
        self.ssh_cons.exec_command("chmod 777 -R /usr/tideway/TKU/")
        log.info("Installing and activating pattern modules. Result:\n")
        if file_check:
            _, stdout, stderr = self.ssh_cons.exec_command("/usr/tideway/bin/tw_pattern_management -p system "
                                                           "--install-activate /usr/tideway/TKU/Tpl_DEV/*")
        else:
            log.error("Checksum of remote \\ local files is not equal! Upload process was probably corrupted!")

        if stdout:
            output = stdout.readlines()
            for elem in output:
                if upload_activated_check.match(elem):
                    uploaded_activated = True
                    log.info("Upload activating:" + "PASSED!")
                    log.info("Pattern uploaded successfully. Module:" + str(module_name))
                else:
                    log.error("Pattern activation failed! Scan will not start.")
                # ssh.close()

        return output, uploaded_activated

    def check_folders(self, path):
        """
        Check if folders created, create if needed
        Folders to check:
        /usr/tideway/TKU/
        /usr/tideway/TKU/Tpl_DEV/
        /usr/tideway/TKU/DML
        /usr/tideway/TKU/TKU_upd
        /usr/tideway/TKU/REC_data

        If no folder:
        Error: ['ls: cannot access /usr/tideway/XYZ: No such file or directory\n']

        :param path: path to check
        """

        log = self.logging

        folders = []
        ftp = self.ssh_cons.open_sftp()
        _, stdout, stderr = self.ssh_cons.exec_command("ls " + path)
        output_ok = stdout.readlines()
        output_err = stderr.readlines()
        if output_err:
            if "No such file or directory" in output_err[0]:
                log.debug("Creating folder: " + path)
                ftp.mkdir(path)
                self.ssh_cons.exec_command("chmod 777 -R " + path)
                log.debug("Folder created!")
            else:
                log.warn("ls command cannot be run on this folder or output is incorrect!")
                folders = False

        if output_ok:
            for folder in output_ok:
                folders.append(folder.strip('\n'))

            log.debug("Folder exist! Content: " + " " * 34 + ', '.join(folders))

        return folders

    def check_file_pattern(self, local_file, remote_file):
        """
        Check the file sum to ensure it was downloaded successfully.

        Pattern:
        output_ok = ['be890ee8bee5f136ca10c03095e8ad60  /usr/tideway/TKU/Tpl_DEV/BMCRemedyARSystem.tpl\n']
        local_hash5 = be890ee8bee5f136ca10c03095e8ad60

        zip:
        output_ok = ['cc625d0ae7ea33885b6c1e7f67bcbf84  /usr/tideway/TKU/Tpl_DEV/BMCRemedyARSystem.zip\n']
        local_hash5 = cc625d0ae7ea33885b6c1e7f67bcbf84

        :param remote_file: file on ADDM
        :param local_file: file in local system
        :return:
        """
        log = self.logging

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
