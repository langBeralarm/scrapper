import custom_utils
import logging.handlers
import os

from datetime import datetime
from freezegun import freeze_time
from unittest import mock, TestCase


class TestTimedCompressionRotatingFileHandler(TestCase):
    DAY = 24 * 60 * 60
    FILE_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs", "test.log")

    def setUp(self):
        self.custom_handler = custom_utils.TimedCompressionRotatingFileHandler(filename=self.FILE_NAME)
        self.handler = logging.handlers.TimedRotatingFileHandler(filename=self.FILE_NAME)

    def tearDown(self):
        del self.custom_handler
        del self.handler
        os.remove(self.FILE_NAME)

    def test_rollover_1(self):
        self._test_custom_compute_rollover("2023-01-10 00:00:00", 21)

    def test_rollover_2(self):
        self._test_custom_compute_rollover("2018-08-16 06:19:26", 15)

    def test_rollover_3(self):
        self._test_custom_compute_rollover("2023-12-31 14:30:47", 0)

    def test_rollover_4(self):
        self._test_custom_compute_rollover("2023-02-15 00:00:00", 13)

    def test_rollover_5(self):
        self._test_custom_compute_rollover("2021-02-01 00:00:00", 27)

    def test_rollover_leap_year_1(self):
        self._test_custom_compute_rollover("2020-02-10 00:00:00", 19)

    def test_rollover_leap_year_2(self):
        self._test_custom_compute_rollover("2024-02-03 00:00:00", 26)

    def _test_custom_compute_rollover(self, time: str, expected_days: int):
        with freeze_time(time):
            test_date = datetime.now()
            test_ts = int(datetime.timestamp(test_date))
            expected = (expected_days * self.DAY) + self.handler.computeRollover(test_ts)

            self.assertEqual(expected, self.custom_handler.computeRollover(test_ts))
