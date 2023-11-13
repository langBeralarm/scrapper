from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from scrapper.celery import eval_task


class CeleryTasksTest(TestCase):
    @patch("scrapper.celery.save_exec_times")
    def test_eval_task_1(self, save_exec_times: MagicMock):
        # Arrange
        now: datetime = datetime.now()
        # Act
        eval_task(10, now)
        # Assert
        save_exec_times.assert_called_with(now, None)

    @patch("scrapper.celery.save_exec_times")
    def test_eval_task_2(self, save_exec_times: MagicMock):
        # Arrange
        now: datetime = datetime.now()
        # Act
        eval_task(100, now)
        # Assert
        save_exec_times.assert_called_with(now, None)
