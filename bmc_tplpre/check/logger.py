"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import logging
from check.local_logic import LocalLogic


def log_define(args):

    """
    Set the proper log level based on arguments.
    Used for python standard logging module.
    Check for typos and handle them.

    :return: proper level for use in logger
    """
    log_lvl = args.log_lvl
    assert isinstance(log_lvl, str)

    path_logic = LocalLogic()
    path_args = path_logic.file_path_decisions(full_file_path=args.full_path)

    try:
        log_path = path_args['working_dir']
    except TypeError as e:
        log_path = ""
        print("Working dir cannot be obtained. WIll save log to module folder: bmc_tplpre/")
        print(e)

    if log_lvl:
        if "info" in log_lvl:
            return i_log(level='INFO', log_path=log_path)
        elif "warning" in log_lvl:
            return i_log(level='WARN', log_path=log_path)
        elif "error" in log_lvl:
            return i_log(level='ERROR', log_path=log_path)
        elif "critical" in log_lvl:
            return i_log(level='CRITICAL', log_path=log_path)
        elif "debug" in log_lvl:
            return i_log(level='DEBUG', log_path=log_path)
        else:
            return i_log(level='INFO', log_path=log_path)
    else:
        return i_log(level='DEBUG', log_path=log_path)


def i_log(level, log_path):
    """
    Logger settings composer.
    If log set to debug - use different file for output.

    :param level: logging level
    :param log_path: path to working dir
    :return:
    """
    assert isinstance(level, str)

    # Logger:
    log = logging.getLogger(__name__)
    log.setLevel(level)
    # Usual logging to file:
    file_handler = logging.FileHandler(log_path+'\\check.log')
    file_handler.setLevel(level)
    # Usual logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    file_formatter = logging.Formatter('%(asctime)-24s'
                                       '%(levelname)-8s '
                                       ' - %(message)-8s')

    console_formatter = logging.Formatter('%(asctime)-24s'
                                          '%(levelname)-9s'
                                          '%(message)8s')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    if level == 'DEBUG':
        # Extra detailed logging to file:
        file_extra_handler = logging.FileHandler(log_path+'\\step.log')
        file_extra_handler.setLevel(logging.DEBUG)
        # Extra detailed logging to console
        con_extra_handler = logging.StreamHandler()
        con_extra_handler.setLevel(logging.DEBUG)

        file_extra_formatter = logging.Formatter('%(asctime)-24s'
                                                 '%(levelname)-8s '
                                                 '%(filename)-21s'
                                                 '%(funcName)-22s'
                                                 'L:%(lineno)-6s'
                                                 '%(message)8s')

        con_extra_formatter = logging.Formatter('%(asctime)-24s'
                                                '%(levelname)-9s'
                                                '%(module)-21s'
                                                '%(funcName)-22s'
                                                'L:%(lineno)-6s'
                                                '%(message)8s')

        file_extra_handler.setFormatter(file_extra_formatter)
        con_extra_handler.setFormatter(con_extra_formatter)

        log.addHandler(file_extra_handler)
        log.addHandler(con_extra_handler)
    else:
        log.addHandler(file_handler)
        log.addHandler(console_handler)

    return log
