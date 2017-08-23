"""
Alexander Danylchenko 2017
TPL - (tideway pattern language) syntax highlighting and checking tool.
Syntax checking is based on BMC code and not included in this public version due to license restrictions.
Allows you to automate usual routine in pattern development.
"""

import logging


class Logger:

    def __init__(self, log_args):

        self.log_lvl = log_args

    def log_define(self):

        """
        Set the proper log level based on arguments.
        Used for python standard logging module.
        Check for typos and handle them.

        :param log_lvl: Input from args  # info, quiet, warn, debug, output, error
        :return: proper level for use in logger
        """

        if self.log_lvl:
            if "info" in self.log_lvl:
                return Logger.i_log(self, level='INFO')
            elif "warn" in self.log_lvl:
                return Logger.i_log(self, level='WARN')
            elif "error" in self.log_lvl:
                return Logger.i_log(self, level='ERROR')
            elif "critical" in self.log_lvl:
                return Logger.i_log(self, level='CRITICAL')
            elif "debug" in self.log_lvl:
                return Logger.i_log(self, level='DEBUG')
            else:
                return Logger.i_log(self, level='INFO')
        else:
            return Logger.i_log(self, level='DEBUG')

    def i_log(self, level):
        """

        :param level: logging level
        :param name: Name of working in class\function
        :return:
        """

        name = __name__

        # Logger:
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # Usual logging to file:
        file_handler = logging.FileHandler('check.log')
        file_handler.setLevel(level)
        # Usual logging to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Extra detailed logging to file:
        file_extra_handler = logging.FileHandler('step.log')
        file_extra_handler.setLevel(logging.DEBUG)
        # Extra detailed logging to console
        con_extra_handler = logging.StreamHandler()
        con_extra_handler.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter('%(asctime)-24s'
                                                '%(levelname)-8s '
                                                ' - %(message)-8s')

        console_formatter = logging.Formatter('%(asctime)-24s'
                                                   '%(levelname)-9s'
                                                   '%(message)8s')

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

        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)

        file_extra_handler.setFormatter(file_extra_formatter)
        con_extra_handler.setFormatter(con_extra_formatter)

        if level == 'DEBUG':
            logger.addHandler(file_extra_handler)
            logger.addHandler(con_extra_handler)
        else:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        return logger
