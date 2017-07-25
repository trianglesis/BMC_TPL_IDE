import hashlib
import os
import re
import zipfile


from check.logger import i_log
log = i_log(level='DEBUG', name=__name__)

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

Additional scenario:
Can upload anything opened in Sublime with path to folder or pattern.
If there is no -tpl arg BUT addm IP.

'''


def upload_knowledge(ssh, pattern_name, dir_label, file_path):
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

    :param ssh:
    :param pattern_name: str
    :param dir_label: str
    :param file_path: str
    """

    messages = []
    output = ''
    zip_path = ''
    upload_activated_check = re.compile('\d+\sknowledge\supload\sactivated')

    _, stdout, stderr = ssh.exec_command("rm -rf /usr/tideway/TKU/Tpl_DEV/*")  # Wipe previous tpl dev uploads
    # Start FTP session with ADDM machine:
    if pattern_name:
        module_name = pattern_name
        messages.append(
                {"log": "info", "msg": "INFO: Upload pattern to ADDM folder:" + " " * 28 + "/usr/tideway/TKU/Tpl_DEV/"})
        localpath = '/usr/tideway/TKU/Tpl_DEV/' + module_name + '.tpl'
        ftp = ssh.open_sftp()
        try:
            ftp.put(file_path, localpath)
            ftp.close()
        except:
            messages.append({"log": "error", "msg": "ERROR: Something goes wrong with ftp connection or zip file!\n"
                                                    "Check if file path or folder exists"})
    else:
        messages.append({"log": "info", "msg": "INFO: Making zip of all .tpl in folder:" + " " * 25 + file_path})
        messages.append(
                {"log": "info", "msg": "INFO: Upload zip to ADDM folder:" + " " * 32 + "/usr/tideway/TKU/Tpl_DEV/"})

        module_name = dir_label
        zipFilename = module_name + '.zip'
        zip_path = file_path + zipFilename
        patternsZip = zipfile.ZipFile(zip_path, 'w')
        messages.append({"log": "debug", "msg": "DEBUG: zipFilename:" + " " * 45 + zipFilename})

        for foldername, subfolders, filenames in os.walk(file_path):
            for filename in filenames:
                if filename != zipFilename:
                    patternsZip.write(os.path.join(file_path, filename), arcname=filename)
                    messages.append({"log": "debug", "msg": "DEBUG: Adding pattern:" + " " * 42 + filename})
        patternsZip.close()

        messages.append({"log": "info", "msg": "INFO: zip_path:" + " " * 48 + zip_path})
        localpath = '/usr/tideway/TKU/Tpl_DEV/' + zipFilename
        ftp = ssh.open_sftp()
        try:
            ftp.put(zip_path, localpath)
            ftp.close()
            messages.append({"log": "info", "msg": "INFO: Patterns zip to ADDM upload:" + " " * 30 + "PASSED!"})
        except:
            messages.append({"log": "error", "msg": "ERROR: Something goes wrong with ftp connection or zip file!\n"
                                                    "Check if file path or folder exists"})

    if zip_path:
        file_check, msg = check_file_pattern(local_file=zip_path, remote_file=localpath, ssh=ssh)
        messages.append(msg[0])
    else:
        file_check, msg = check_file_pattern(local_file=file_path, remote_file=localpath, ssh=ssh)
        messages.append(msg[0])

    uploaded_activated = False  # 1 knowledge upload activated
    ssh.exec_command("chmod 777 -R /usr/tideway/TKU/")
    messages.append({"log": "debug", "msg": "=" * 150 + "\nINFO: Installing and activating pattern modules. Result:\n"})
    if file_check:
        _, stdout, stderr = ssh.exec_command("/usr/tideway/bin/tw_pattern_management -p system --install-activate "
                                             "/usr/tideway/TKU/Tpl_DEV/*")
    else:
        messages.append({"log": "error",
                         "msg": "ERROR: Checksum of remote \\ "
                                "local files is not equal! Upload process was probably corrupted!"})

    if stdout:
        output = stdout.readlines()
        for elem in output:
            messages.append({"log": "debug", "msg": elem.strip('\n')})
            if upload_activated_check.match(elem):
                uploaded_activated = True
                messages.append({"log": "info", "msg": "INFO: Upload activating:" + " " * 40 + "PASSED!"})
                messages.append({"log": "info", "msg": "INFO: Pattern uploaded successfully. "
                                                       "Module:" + " " * 20 + str(module_name)})
                # else:
                #     messages.append({"log":"error", "msg":"ERROR: Pattern activation failed! Scan will not start."})
                # ssh.close()

    return output, uploaded_activated, messages


def check_folders(path, ssh):
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

    :param ssh: opened ssh session
    :param path: path to check
    """

    messages = []
    folders = []
    ftp = ssh.open_sftp()
    _, stdout, stderr = ssh.exec_command("ls " + path)
    output_ok = stdout.readlines()
    output_err = stderr.readlines()
    if output_err:
        if "No such file or directory" in output_err[0]:
            messages.append({"log": "debug", "msg": "DEBUG: Creating folder: " + path})
            ftp.mkdir(path)
            ssh.exec_command("chmod 777 -R " + path)
            messages.append({"log": "debug", "msg": "DEBUG: Folder created!"})
        else:
            messages.append(
                    {"log": "warn", "msg": "WARN: ls command cannot be run on this folder or output is incorrect!"})
            folders = False

    if output_ok:
        for folder in output_ok:
            folders.append(folder.strip('\n'))

        messages.append({"log": "debug", "msg": "DEBUG: Folder exist! Content: " + " " * 34 + ', '.join(folders)})

    return folders, messages


def check_file_pattern(local_file, remote_file, ssh):
    """
    Check the file sum to ensure it was downloaded successfully.

    Pattern:
    output_ok = ['be890ee8bee5f136ca10c03095e8ad60  /usr/tideway/TKU/Tpl_DEV/BMCRemedyARSystem.tpl\n']
    local_hash5 = be890ee8bee5f136ca10c03095e8ad60

    zip:
    output_ok = ['cc625d0ae7ea33885b6c1e7f67bcbf84  /usr/tideway/TKU/Tpl_DEV/BMCRemedyARSystem.zip\n']
    local_hash5 = cc625d0ae7ea33885b6c1e7f67bcbf84

    :param ssh: opened SSH session
    :param remote_file: file on ADDM
    :param local_file: file in local system
    :return:
    """
    messages = []
    local_hash5 = hashlib.md5(open(local_file, 'rb').read()).hexdigest()
    _, stdout, stderr = ssh.exec_command("md5sum " + remote_file)
    output_ok = stdout.readlines()

    if local_hash5 in output_ok[0]:
        messages.append({"log": "debug",
                         "msg": "DEBUG: Checksum of files is OK!\n "
                                "Local sum:  " + local_hash5 + "\n Remote sum: " + output_ok[0]})
        file_ok = True
    else:
        messages.append({"log": "debug",
                         "msg": "DEBUG: Checksum of files is DIFFERENT!\n "
                                "Local sum: " + local_hash5 + "\n Remote sum: " + output_ok[0]})
        file_ok = False

    return file_ok, messages
