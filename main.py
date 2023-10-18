import logging.config
import os

import random
import string
import time

from utils import TimedCompressionRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - [%(levelname)s] - %(name)s - %(pathname)s.(%(funcName)s):%(lineno)d - %(message)s",  # noqa: E501
            "class": "utils.UTCFormatter",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "utils.TimedCompressionRotatingFileHandler",
            "filename": os.path.join(BASE_DIR, 'logs/atas', 'atas.log'),
            "when": "S",  # "when": "midnight",
            "interval": 30,
            "backupCount": 3,
            "utc": True,
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "": {
            "handlers": ["console", "default"],
            "level": "INFO",
        },
    },
}

# defaultHandler = logging.handlers.TimedRotatingFileHandler(
#     os.path.join(BASE_DIR, 'logs/atas', 'atas.log'),
#     'midnight',
#     backupCount=365
# )
# defaultHandler.rotator = rotator

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def custom_add(x: int, y: int) -> int:
    """
    Adds two ints and returns the sum.
    """
    return x + y


if __name__ == "__main__":
    logger.info('This is a test!')
    res: int = custom_add(4, 5)  # pragma: no cover
    t = TimedCompressionRotatingFileHandler(filename=os.path.join(BASE_DIR, 'logs/atas', 'atas.log'))
    while True:
        msg = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 15)))
        logger.info(msg)
        current_time = int(time.time())
        print(f'Rollover time: {((t.computeRollover(current_time) - current_time) / (24 * 60 * 60))}')
        time.sleep(2)



