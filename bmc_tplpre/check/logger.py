

import logging


def i_log(level=None, name=None):
    """

    :param level:
    :param name:
    :return:
    """
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
                                             'Line:%(lineno)-4s'
                                             ' - %(message)-8s')

    con_extra_formatter = logging.Formatter('%(asctime)-24s'
                                            '%(levelname)-9s'
                                            '%(name)-22s'
                                            '%(funcName)-28s'
                                            'Line:%(lineno)-4s'
                                            '%(message)8s')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    file_extra_handler.setFormatter(file_extra_formatter)
    con_extra_handler.setFormatter(con_extra_formatter)

    # logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    logger.addHandler(file_extra_handler)
    logger.addHandler(con_extra_handler)

    return logger

