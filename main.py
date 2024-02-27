import logging.config
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Setup logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            # pylint: disable=C0301
            "format": "%(asctime)s - [%(levelname)s] - %(name)s - %(pathname)s.(%(funcName)s):%(lineno)d - %(message)s",  # noqa: E501
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
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/general", "general.log"),
            "when": "midnight",
            "backupCount": 30,
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

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def custom_add(x: int, y: int) -> int:
    """
    Adds two ints and returns the sum.
    """
    return x + y


if __name__ == "__main__":
    res: int = custom_add(4, 5)  # pragma: no cover
