import glob
import os
import unittest
import zipfile
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from freezegun import freeze_time  # type: ignore

from jobs import (
    _get_files_to_zip,
    _group_log_files,
    _remove_zip_files,
    _skip_file,
    _zip_files,
    clean_log_files,
)
from main import BASE_DIR


# TODO: Clean up tests pylint: disable=fixme
class TestJobs(unittest.TestCase):
    CURRENT_DIR: str = os.path.dirname(os.path.realpath(__file__))

    def test_skip_file_1(self):
        # Arrange
        file: str = "some/path"
        # Assert
        self.assertTrue(_skip_file(file))

    def test_skip_file_2(self):
        # Arrange
        file_path: str = self.CURRENT_DIR + "/test.log"
        # Act
        open(file_path, "w").close()
        # Assert
        self.assertFalse(_skip_file(file_path))
        # Cleanup
        os.remove(file_path)

    def test_skip_file_zip_1(self):
        # Arrange
        file_path: str = self.CURRENT_DIR + "/test.log.zip"
        # Act
        zipfile.ZipFile(file_path, "w").close()
        # Assert
        self.assertTrue(_skip_file(file_path))
        # Cleanup
        os.remove(file_path)

    def test_skip_file_zip_2(self):
        # Arrange
        file_path: str = self.CURRENT_DIR + "/test.log.zip"
        # Act
        zipfile.ZipFile(file_path, "w").close()
        # Assert
        self.assertFalse(_skip_file(file_path, include_zip=True))
        # Cleanup
        os.remove(file_path)

    def test_grouped_files_1(self):
        # Arrange
        files: list[str] = [
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-10-11",
            "some/path/logger2.log.2022-12-02",
            "some/path/logger2.log.2022-12-03",
        ]
        # Act
        grouped_files: dict[str, list[str]] = _group_log_files(files)
        # Assert
        self.assertEqual(grouped_files, {})

    def test_grouped_files_2(self):
        # Arrange
        files: list[str] = [
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-11",
            self.CURRENT_DIR + "/logger2.log.2022-12-02",
            self.CURRENT_DIR + "/logger2.log.2022-12-03",
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
        ]
        for file in files:
            open(file, "w").close()
        # Act
        grouped_files: dict[str, list[str]] = _group_log_files(files)
        # Assert
        expected: dict[str, list[str]] = {
            "logger1": [
                self.CURRENT_DIR + "/logger1.log.2023-10-10",
                self.CURRENT_DIR + "/logger1.log.2023-10-11",
            ],
            "logger2": [
                self.CURRENT_DIR + "/logger2.log.2022-12-02",
                self.CURRENT_DIR + "/logger2.log.2022-12-03",
            ],
        }
        self.assertEqual(grouped_files, expected)
        # Cleanup
        for file in files:
            if os.path.isfile(file):
                os.remove(file)

    def test_get_files_to_zip_1(self):
        # Arrange
        files: list[str] = [
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-10-11",
            "some/path/logger2.log.2022-12-02",
            "some/path/logger2.log.2022-12-03",
        ]
        # Act
        files_to_zip: list[str] = _get_files_to_zip(files, "2023-10")
        # Assert
        self.assertEqual(files_to_zip, [])

    def test_get_files_to_zip_2(self):
        # Arrange
        files: list[str] = [
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-11",
            self.CURRENT_DIR + "/logger2.log.2022-12-02",
            self.CURRENT_DIR + "/logger2.log.2022-12-03",
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-11-10",
            self.CURRENT_DIR + "/logger1.log.2023-11-23",
        ]
        for file in files:
            open(file, "w").close()
        # Act
        files_to_zip: list[str] = _get_files_to_zip(files, "2023-10")
        # Assert
        expected: list[str] = [
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-11",
        ]
        self.assertEqual(files_to_zip, expected)
        # Cleanup
        for file in files:
            if os.path.isfile(file):
                os.remove(file)

    def test_get_files_to_zip_3(self):
        # Arrange
        files: list[str] = [
            self.CURRENT_DIR + "/logger1.log.2022-10-10",
            self.CURRENT_DIR + "/logger1.log.2021-10-10",
            self.CURRENT_DIR + "/logger1.log.2022-10-11",
            self.CURRENT_DIR + "/logger2.log.2024-12-02",
            self.CURRENT_DIR + "/logger2.log.2019-12-03",
            self.CURRENT_DIR + "/logger1.log.2021-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-11-10",
            self.CURRENT_DIR + "/logger1.log.2022-10-05",
        ]
        for file in files:
            open(file, "w").close()
        # Act
        files_to_zip: list[str] = _get_files_to_zip(files, "2022-10")
        # Assert
        expected: list[str] = [
            self.CURRENT_DIR + "/logger1.log.2022-10-10",
            self.CURRENT_DIR + "/logger1.log.2022-10-11",
            self.CURRENT_DIR + "/logger1.log.2022-10-05",
        ]
        self.assertEqual(files_to_zip, expected)
        # Cleanup
        for file in files:
            if os.path.isfile(file):
                os.remove(file)

    def test_zip_files(self):
        # Arrange
        zipfile_count_before: int = len(
            glob.glob(self.CURRENT_DIR + "/**/*.logs.zip**", recursive=True)
        )
        files: list[str] = [
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
            self.CURRENT_DIR + "/logger1.log.2023-10-11",
            self.CURRENT_DIR + "/logger2.log.2022-12-02",
            self.CURRENT_DIR + "/logger2.log.2022-12-03",
            self.CURRENT_DIR + "/logger1.log.2023-10-10",
        ]
        file_location: str = self.CURRENT_DIR + "/YYYY-MM-DD.logger.logs.zip"
        for file in files:
            open(file, "w").close()
        # Act
        _zip_files(files, file_location)
        # Assert
        zipfile_count_after: int = len(
            glob.glob(self.CURRENT_DIR + "/**/*.logs.zip**", recursive=True)
        )
        self.assertEqual(zipfile_count_after, zipfile_count_before + 1)
        for file in files:
            self.assertFalse(os.path.exists(file))
        # TODO: Check if files in zip exist?
        # Cleanup
        if os.path.isfile(file_location):
            os.remove(file_location)

    def test_remove_zip_files(self):
        # Arrange
        zipfile_count_before: int = len(
            glob.glob(self.CURRENT_DIR + "/**/*.logs.zip**", recursive=True)
        )
        zip_files: list[str] = [
            self.CURRENT_DIR + "/2023-10.logger.logs.zip",
            self.CURRENT_DIR + "/2023-01.logger.logs.zip",
            self.CURRENT_DIR + "/2023-09.logger.logs.zip",
            self.CURRENT_DIR + "/2022-12.logger.logs.zip",
            self.CURRENT_DIR + "/2022-12.logger.logs.zip",
            self.CURRENT_DIR + "/2023-03.logger.logs.zip",
        ]
        for zip_file in zip_files:
            zipfile.ZipFile(zip_file, "w").close()
        cleanup_dt: datetime = datetime(2023, 9, 1)
        # Act
        _remove_zip_files(zip_files, cleanup_dt)
        # Assert
        zipfile_count_after: int = len(
            glob.glob(self.CURRENT_DIR + "/**/*.logs.zip**", recursive=True)
        )
        self.assertEqual(zipfile_count_after, zipfile_count_before + 2)
        # Cleanup
        for file in zip_files:
            if os.path.isfile(file):
                os.remove(file)

    @patch("glob.glob")
    @patch("jobs._remove_zip_files")
    @patch("jobs._zip_files")
    @patch("jobs._group_log_files")
    @patch("jobs._get_files_to_zip")
    def test_clean_log_files_1(
        self,
        get_zip_files: MagicMock,
        group_log_files: MagicMock,
        zip_files: MagicMock,
        remove_zip_files: MagicMock,
        glob_: MagicMock,
    ):
        # Arrange
        glob_.return_value = []
        # Act
        with freeze_time("2023-10-10"):
            clean_log_files()
        # Assert
        get_zip_files.assert_called_once_with([], "2023-09")
        assert zip_files.call_count == 0
        with freeze_time("2022-09-30"):
            remove_zip_files.assert_called_once_with(
                glob.glob("gugus"), datetime.now(timezone.utc), "%Y-%m"
            )

    @patch("glob.glob")
    @patch("jobs._remove_zip_files")
    @patch("jobs._zip_files")
    @patch("jobs._skip_file")
    def test_clean_log_files_2(
        self,
        skip_file: MagicMock,
        zip_files: MagicMock,
        remove_zip_files: MagicMock,
        glob_: MagicMock,
    ):
        # Arrange
        skip_file.return_value = False
        files: list[str] = [
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-10-11",
            "some/path/logger2.log.2022-12-02",
            "some/path/logger2.log.2022-12-03",
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-11-07",
            "some/path/logger1.log.2023-11-10",
        ]
        glob_.return_value = files
        # Act
        with freeze_time("2023-11-10"):
            clean_log_files()
        # Assert
        file_path: str = os.path.join(
            BASE_DIR, "logs", "logger1", "2023-10.logger1.logs.zip"
        )
        args, kwargs = zip_files.call_args_list[0]
        self.assertEqual(
            args[0],
            ["some/path/logger1.log.2023-10-10", "some/path/logger1.log.2023-10-11"],
        )
        self.assertEqual(args[1], file_path)
        with freeze_time("2022-10-31"):
            remove_zip_files.assert_called_once_with(
                files, datetime.now(timezone.utc), "%Y-%m"
            )

    @patch("glob.glob")
    @patch("jobs._remove_zip_files")
    @patch("jobs._zip_files")
    @patch("jobs._skip_file")
    def test_clean_log_files_3(
        self,
        skip_file: MagicMock,
        zip_files: MagicMock,
        remove_zip_files: MagicMock,
        glob_: MagicMock,
    ):
        # Arrange
        skip_file.return_value = False
        files: list[str] = [
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-10-11",
            "some/path/logger2.log.2023-10-02",
            "some/path/logger2.log.2023-10-03",
            "some/path/logger1.log.2023-10-10",
            "some/path/logger1.log.2023-11-07",
            "some/path/logger1.log.2023-11-10",
        ]
        glob_.return_value = files
        # Act
        with freeze_time("2023-11-10"):
            clean_log_files()
        # Assert
        file_path: str = os.path.join(
            BASE_DIR, "logs", "logger1", "2023-10.logger1.logs.zip"
        )
        args, kwargs = zip_files.call_args_list[0]
        self.assertEqual(
            args[0],
            ["some/path/logger1.log.2023-10-10", "some/path/logger1.log.2023-10-11"],
        )
        self.assertEqual(args[1], file_path)
        file_path = os.path.join(
            BASE_DIR, "logs", "logger2", "2023-10.logger2.logs.zip"
        )
        args, kwargs = zip_files.call_args_list[1]
        self.assertEqual(
            args[0],
            ["some/path/logger2.log.2023-10-02", "some/path/logger2.log.2023-10-03"],
        )
        self.assertEqual(args[1], file_path)
        with freeze_time("2022-10-31"):
            remove_zip_files.assert_called_once_with(
                files, datetime.now(timezone.utc), "%Y-%m"
            )
