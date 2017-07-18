import logging


def config_log_lvl(log_lvl):
    """

    :return:
    """
    logger = logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname) %(funcName)s -8s [%(asctime)s]  %(message)s', level = logging.DEBUG, filename = u'check.log')

    return logger