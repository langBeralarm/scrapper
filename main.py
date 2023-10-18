import logging.config
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

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
        # "default": {
        #     "level": "INFO",
        #     "formatter": "standard",
        #     "class": "logging.handlers.TimedRotatingFileHandler",
        #     "filename": f"{base_dir}/logs/atas.log",
        #     "when": "midnight",
        #     "backupCount": 365,
        # },
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        # "": {
        #     "handlers": ["console", "default"],
        #     "level": "INFO",
        # },
    },
}

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
