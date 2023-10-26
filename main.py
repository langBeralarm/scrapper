import logging.config
import time

from random_word import RandomWords  # type: ignore

from tasks import alert, notify

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
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
    },
    "loggers": {
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    r = RandomWords()
    for i in range(10, 0, -1):
        message: str = f"{r.get_random_word()} - {i}"
        recipient: str = r.get_random_word()
        countdown: int = i * 2
        logger.info(
            "Message: %s - Recipient: %s - Countdown: %d"
            % (message, recipient, countdown)
        )
        # The comma in the args is necessary otherwise an error occurs
        alert.apply_async((message,), link=notify.s(recipient), countdown=countdown)
        time.sleep(1)
