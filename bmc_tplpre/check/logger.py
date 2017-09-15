"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import logging


def log_define(log_lvl):

    """
    Set the proper log level based on arguments.
    Used for python standard logging module.
    Check for typos and handle them.

    :return: proper level for use in logger
    """
    assert isinstance(log_lvl, str)

    if log_lvl:
        if "info" in log_lvl:
            return i_log(level='INFO')
        elif "warning" in log_lvl:
            return i_log(level='WARN')
        elif "error" in log_lvl:
            return i_log(level='ERROR')
        elif "critical" in log_lvl:
            return i_log(level='CRITICAL')
        elif "debug" in log_lvl:
            return i_log(level='DEBUG')
        else:
            return i_log(level='INFO')
    else:
        return i_log(level='DEBUG')


def i_log(level):
    """

    :param level: logging level
    :return:
    """
    assert isinstance(level, str)

    # Logger:
    log = logging.getLogger(__name__)
    log.setLevel(level)
    # Usual logging to file:
    file_handler = logging.FileHandler('check.log')
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
        file_extra_handler = logging.FileHandler('step.log')
        file_extra_handler.setLevel(logging.DEBUG)
        # Extra detailed logging to console
        con_extra_handler = logging.StreamHandler()
        con_extra_handler.setLevel(logging.DEBUG)

        file_extra_formatter = logging.Formatter('%(asctime)-24s'
                                                 '%(levelname)-8s '
                                                 '%(name)-21s'
                                                 '%(filename)-18s'
                                                 '%(funcName)-28s'
                                                 'Line:%(lineno)-6s'
                                                 ' - %(message)-8s')

        con_extra_formatter = logging.Formatter('%(asctime)-24s'
                                                '%(levelname)-9s'
                                                '%(funcName)-28s'
                                                'Line:%(lineno)-6s'
                                                '%(message)8s')

        file_extra_handler.setFormatter(file_extra_formatter)
        con_extra_handler.setFormatter(con_extra_formatter)

        log.addHandler(file_extra_handler)
        log.addHandler(con_extra_handler)
    else:
        log.addHandler(file_handler)
        log.addHandler(console_handler)

    return log
