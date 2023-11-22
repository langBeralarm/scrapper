import os
from datetime import datetime, timezone
from typing import Optional

from celery import Celery  # type: ignore
from celery.utils.log import get_task_logger  # type: ignore

logger = get_task_logger(__name__)

is_redis_broker = os.environ.get("REDIS")
if is_redis_broker:
    app = Celery("scrapper", broker="redis://redis:6379/1", include=["scrapper"])
else:
    app = Celery(
        "scrapper", broker="amqp://guest:guest@rabbit:5672/1", include=["scrapper"]
    )

TIMEOUT: int = (24 * 60 * 60) + 1

if app is not None and not is_redis_broker:
    # Celery configuration
    app.conf.update(
        task_time_limit=TIMEOUT,  # For long-running tasks of up to 24 hours
        worker_hijack_root_logger=False,  # Celery shouldn't overwrite the root logger
        # Sensible defaults for task annotations
        task_annotations={
            "*": {
                "ignore_result": True,  # Requires explicitly enabling results
            }
        },
        worker_log_format="%(asctime)s - [%(levelname)s] - %(name)s/%(processName)s - %(message)s",  # noqa: E501 pylint: disable=line-too-long
        # Need to call get_task_logger to apply the following format
        worker_task_log_format="%(asctime)s - [%(levelname)s] - %(name)s - %(pathname)s.(%(funcName)s):%(lineno)d - %(message)s",  # noqa: E501 pylint: disable=line-too-long
        worker_task_stoudts_level="INFO",
        # For testing with task_acks_late
        # task_acks_late=True,
        # task_acks_on_failure_or_timeout=False,
        # worker_deduplicate_successful_tasks=True,
        result_backend="redis://redis:6379/0",
        # result_backend_transport_options={},
        # For testing other configs
        # result_backend_thread_safe=True,
        # broker_heartbeat, Found no good answers on the internet
        # broker_pool_limit= Leave default since we aren't using eventlet/gevent
        # worker_cancel_long_running_tasks_on_connection_loss,
        # RabbitMQ specific
        # broker_login_method,  Default seems okay
        broker_connection_retry_on_startup=True,
        # Explicitly set allowed content types
        accept_content=("json",),
    )
else:
    app.conf.update(
        task_time_limit=TIMEOUT,  # For long-running tasks of up to 24 hours
        worker_hijack_root_logger=False,  # Celery shouldn't overwrite the root logger
        # Sensible defaults for task annotations
        task_annotations={
            "*": {
                "ignore_result": True,  # Requires explicitly enabling results
            }
        },
        worker_log_format="%(asctime)s - [%(levelname)s] - %(name)s/%(processName)s - %(message)s",  # noqa: E501 pylint: disable=line-too-long
        # Need to call get_task_logger to apply the following format
        worker_task_log_format="%(asctime)s - [%(levelname)s] - %(name)s - %(pathname)s.(%(funcName)s):%(lineno)d - %(message)s",  # noqa: E501 pylint: disable=line-too-long
        worker_task_stoudts_level="INFO",
        result_backend="redis://redis:6379/0",
        result_backend_transport_options={"visibility_timeout": TIMEOUT},
        # Explicitly set allowed content types
        accept_content=("json",),
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
):  # pylint: disable=missing-function-docstring
    del expected_exec
    del actual_exec
