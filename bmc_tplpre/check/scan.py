
'''
1. If pattern module uploaded successfully and activated - start this (input)
1.1 Open saved SSH session if exist. (input)
2. Check or change tw_disco_control (standard|playback|record)
3. Check or start tw_scan_control --start
4. Start scan with passed arguments: pattern_name, host_list
5. Show result, scan ID ect. (output)
'''


def addm_scan(ssh, disco_mode, host_list, dir_label):
    """

    :param ssh:
    :param disco_mode:
    :param host_list:
    :param dir_label:
    :param log_lvl:
    """
    messages = []
    if disco_mode:
        stdin, stdout, stderr = ssh.exec_command("/usr/tideway/bin/tw_disco_control -p system --"+disco_mode)
    else:
        stdin, stdout, stderr = ssh.exec_command("/usr/tideway/bin/tw_disco_control -p system --standard")

    if stdout:
        result = stdout.readlines()
        messages.append({"log":"debug", "msg":"DEBUG: Discovery mode is:"+" "*40+result[0]+"Discovery status:"+" "*47+result[1]})
        messages.append({"log":"info", "msg":"="*150+"\nINFO: Discovery started"})

    messages.append({"log":"info", "msg":"INFO: Host(s) to scan:"+" "*42+host_list})
    messages.append({"log":"info", "msg":"INFO: Scan will be named as:"+" "*36+dir_label})

    ssh.exec_command("/usr/tideway/bin/tw_scan_control -p system --start")
    stdin, stdout, stderr = ssh.exec_command("/usr/tideway/bin/tw_scan_control -p system --add --label="+dir_label+" --loglevel=debug --list "+host_list)
    if stdout:
        result = stdout.read().decode()
        messages.append({"log":"info", "msg":"INFO: Scan has been added to the Currently Processing Runs:\n"+result})

    return messages


def addm_scan_check(ssh, scan_id):
    """
    Check scan status.
    Return when scan is finished.

    [root@localhost bin]# /usr/tideway/bin/tw_scan_control -p system --list-full
    ID                               Enabled Label                 User   Scan type Range
    ef5ced348e3150203c1e7f0000010a76 True    BMCRemedySingleSignOn system Snapshot  137.72.93.138
    [root@localhost bin]# /usr/tideway/bin/tw_scan_control -p system --list-full
    No scan ranges


    :param ssh:
    :param scan_id:
    :return:
    """

def addm_scan_reasoning_on_off(ssh, reasoning_flag):
    """
    Start/Stop reasoning.


    :param ssh:
    :param reasoning_flag:
    :return:
    """