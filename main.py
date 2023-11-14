import logging.config
import os
from datetime import datetime
from time import sleep

from scrapper.celery import eval_task

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - [%(levelname)s] - %(name)s - %(pathname)s.(%(funcName)s):%(lineno)d - %(message)s",  # noqa: E501 pylint: disable=line-too-long
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
            "filename": os.path.join(BASE_DIR, "logs", "celery.log"),
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


if __name__ == "__main__":
    for counter in range(1, 101):
        dt: datetime = datetime.now()
        eval_task.apply_async((counter, dt), countdown=counter)
        logger.info(
            "Called Task with counter: %d at: %s",
            counter,
            dt.strftime("%Y-%m-%d %H:%M:%S,%f"),
        )
        sleep(int(counter / 2))
