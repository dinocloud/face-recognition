import logging
import time

from logging.handlers import RotatingFileHandler

LOGGER = None

MAX_LOGGING_BYTES = 1000000
BACKUP_COUNT = 5
LEVELS = {
    "info" : logging.INFO,
    "error" : logging.ERROR,
    "debug" : logging.DEBUG
}


def create_rotating_log(path, level):
    """
    Creates a rotating log
    """
    logger = logging.getLogger("Hijitus")
    logger.setLevel(LEVELS.get(level, "info"))

    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=MAX_LOGGING_BYTES,
                                  backupCount=BACKUP_COUNT)
    logger.addHandler(handler)
    return logger