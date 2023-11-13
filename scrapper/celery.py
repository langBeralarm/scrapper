import logging
from datetime import datetime, timezone
from typing import Optional

from celery import Celery  # type: ignore

logger = logging.getLogger(__name__)

app = Celery(
    "scrapper", broker="amqp://guest:guest@rabbit:5672/1", include=["scrapper"]
)

# Celery configuration
app.conf.update(
    task_time_limit=24 * 60 * 60,  # For long-running tasks of up to 24 hours
    worker_hijack_root_logger=False,  # Celery shouldn't overwrite the root logger
    # Sensible defaults for task annotations
    task_annotations={
        "*": {
            "ignore_result": True,  # Requires explicitly enabling results
        }
    },
    # For testing
    task_acks_late=True,
    task_acks_on_failure_or_timeout=False,
    worker_deduplicate_successful_tasks=True,
    result_backend="redis://redis:6379/0",
)


@app.task(bind=True)
def eval_task(
    self, counter: int, call_dt: datetime
):  # pylint: disable=missing-function-docstring
    if self.request.eta is not None:  # pragma: no cover
        discrepancy: float = (
            datetime.now(timezone.utc)
            - datetime.strptime(self.request.eta, "%Y-%m-%dT%H:%M:%S.%f%z")
        ).total_seconds()
        logger.info(
            "Called on %s with counter: %s - eta: %s - discrepancy: %s",
            call_dt,
            counter,
            self.request.eta,
            discrepancy,
        )
    save_exec_times(call_dt, self.request.eta)


def save_exec_times(
    expected_exec: datetime, actual_exec: Optional[datetime] = None
):  # pylint: disable=unused-argument, missing-function-docstring
    pass