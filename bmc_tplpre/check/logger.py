

import logging


def i_log(level=None, name=None):
    """

    :param level:
    :param name:
    :return:
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = logging.FileHandler('check.log')
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    file_formatter = logging.Formatter('%(asctime)-24s'
                                       '%(levelname)-8s '
                                       '%(name)-21s'
                                       '%(filename)-18s'
                                       'Line:%(lineno)-4s'
                                       ' - %(message)-8s')

    console_formatter = logging.Formatter('%(asctime)-24s'
                                          '%(levelname)-9s'
                                          '%(name)-22s'
                                          '%(message)8s')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

