import logging
from colorlog import ColoredFormatter
from config import settings


def logger_config(module):
    """
    Logger function. Extends Python loggin module and set a custom config.
    params: Module Name. e.i: logger_config(__name__).
    return: Custom logger_config Object.
    """
    LOGFORMAT = (
        "%(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
    )
    formatter = ColoredFormatter(LOGFORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    custom_logger = logging.getLogger(module)
    custom_logger.setLevel(settings.LOG_LEVEL)

    custom_logger.addHandler(handler)

    return custom_logger
