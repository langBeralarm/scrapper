import logging.handlers
from datetime import datetime, timezone


class UTCFormatter(logging.Formatter):
    """
    A logging Formatter giving timestamps in the ISO 8601 format using the UTC time
    zone designator.
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        # Call the logging Formatter's formatTime method if a datefmt is given
        if datefmt is not None:
            return super().formatTime(record, datefmt)
        # Return the creation time in the UTC timezone including the full time with the
        # fractional seconds truncated to milliseconds
        return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(
            timespec="milliseconds"
        )
