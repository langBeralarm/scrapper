import glob
import os.path
import zipfile
from datetime import datetime, timedelta, timezone


def clean_log_files():
    """
    Clean the log files.

    Add log files of the previous month to a zip file in the same folder and remove
    them afterwards.
    Remove zip files of logs older than a year.
    """
    # Get the root folder of the project
    from main import BASE_DIR  # pylint: disable=import-outside-toplevel,cyclic-import

    # Set default time format
    dt_format: str = "%Y-%m"

    # Get Datetime of previous month
    start_of_month: datetime = datetime.now(timezone.utc).replace(day=1)
    previous_month: datetime = start_of_month - timedelta(days=1)

    # Get log files
    file_names: list[str] = glob.glob(BASE_DIR + "/**/logs/**/*.log**", recursive=True)
    # Get zip files
    zip_files: list[str] = glob.glob(
        BASE_DIR + "/**/logs/**/*.logs.zip**", recursive=True
    )

    # Get files of the previous month
    files_to_zip: list[str] = _get_files_to_zip(
        file_names, previous_month.strftime(dt_format)
    )

    grouped_files: dict[str, list[str]] = _group_log_files(files_to_zip)

    # Create the zip archive with the files of the previous month
    for key, value in grouped_files.items():
        zipfile_name: str = f"{previous_month.strftime(dt_format)}.{key}.logs.zip"
        zipfile_location: str = os.path.join(BASE_DIR, "logs", key, zipfile_name)

        _zip_files(value, zipfile_location)

    # Get clean up datetime one year prior to the previous month
    clean_up_dt: datetime = previous_month.replace(year=previous_month.year - 1)

    _remove_zip_files(zip_files, clean_up_dt, dt_format)


def _get_files_to_zip(files: list[str], previous_month: str) -> list[str]:
    """
    Return a list of file paths matching the given month.

    :param files: List of file paths to filter
    :param previous_month: Given month to filter for
    :return: List of file paths
    """
    files_to_zip: list[str] = []

    for file in files:
        # Guard clause
        if _skip_file(file):
            continue

        if previous_month in str(file) and str(file) not in files_to_zip:
            files_to_zip.append(str(file))

    return files_to_zip


def _zip_files(files: list[str], zipfile_location: str):
    """
    Zip files in the given location and remove the files afterwards.

    :param files: List of file paths to zip
    :param zipfile_location: Location to zip files in
    """
    with zipfile.ZipFile(zipfile_location, "w") as zipf:
        for file in files:
            # Guard clause
            if _skip_file(file):
                continue

            # Get file data
            with open(file) as f:  # pylint: disable=unspecified-encoding
                file_data: str = f.read()

            # Get file name
            file_name: str = file.split("/")[-1]

            # Write file to zip archive
            zipf.writestr(file_name, file_data)

            # Remove the file
            os.remove(file)


def _skip_file(file: str, include_zip=False) -> bool:
    """
    Check if the file should be skipped.

    :param file: File path
    :param include_zip: If True checks ZIP files
    :return: True if file should be skipped, False otherwise
    """
    if include_zip:
        return file is None or not zipfile.is_zipfile(file)

    return file is None or not os.path.isfile(file) or zipfile.is_zipfile(file)


def _remove_zip_files(zip_files: list[str], clean_up_dt: datetime, dt_format="%Y-%m"):
    """
    Remove the zip files older than the given clean_up_dt.

    :param zip_files: List of zip file paths
    :param clean_up_dt: Datetime limit
    :param dt_format: Datetime format
    """
    for file in zip_files:
        # Guard clause
        if _skip_file(file, include_zip=True):
            continue

        # Get creation datetime
        file_dt_part: str = file.split("/")[-1].split(".")[0]
        creation_dt: datetime = datetime.strptime(file_dt_part, dt_format)

        if creation_dt < clean_up_dt:
            os.remove(file)


def _group_log_files(files: list[str]) -> dict[str, list[str]]:
    """
    Group the log files for the same logger.
    :param files: List of file paths
    :return: A dictionary with logger:list of file paths pairs
    """
    grouped_files: dict[str, list[str]] = {}

    for file in files:
        # Guard clause
        if _skip_file(file):
            continue

        # Get log type
        log_type: str = file.split("/")[-1].split(".")[0]

        # Group file path in log type
        if log_type not in grouped_files:
            grouped_files[log_type] = []

        if file not in grouped_files[log_type]:
            grouped_files[log_type].append(file)

    return grouped_files
