import gzip
import logging.handlers
import os
import shutil

from datetime import datetime, timedelta, timezone


class UTCFormatter(logging.Formatter):
    """
    A logging Formatter giving timestamps in the ISO 8601 format using the UTC time zone designator.
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        # Call the logging Formatter's formatTime method if a datefmt is given
        if datefmt is not None:
            return super().formatTime(record, datefmt)
        # Return the creation time in the UTC timezone including the full time with the fractional seconds truncated
        # to milliseconds
        return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(timespec='milliseconds')


class TimedCompressionRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.suffix = self.suffix + ".log"

    def custom_rotator(self, source, dest):
        with open(source, 'rb') as file_in:
            with gzip.open(dest, 'wb') as file_out:
                shutil.copyfileobj(file_in, file_out)
        os.remove(source)

    def custom_namer(self, name):
        return name + ".gz"

    def computeRollover(self, currentTime: int) -> int:
        """
        Work out the rollover time for the end of each month.
        :param currentTime: int
        :return:
        """
        r = super().computeRollover(currentTime)

        current_date = datetime.now()
        next_month = current_date.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)

        if current_date >= last_day:
            return r
        days_delta = (last_day - current_date).days
        return r + (days_delta * (24 * 60 * 60))

    rotator = custom_rotator
    namer = custom_namer
