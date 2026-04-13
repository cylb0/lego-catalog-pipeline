import os
from contextlib import contextmanager
import shutil
from datetime import datetime
import hashlib


def join_path(path: str, filename: str) -> str:
    """
    Join a path and a filename
    Is essentially an alias for os.path.join

    :param path: The path to join
    :param filename: The filename to join
    :return: The joined path
    """
    return os.path.join(path, filename)


def get_filename(path: str) -> str:
    """
    Get the filename from a path

    :param path: The path to get the filename from
    :return: The filename
    """
    return os.path.basename(path)


def create_filename_with_timestamp(filename: str) -> str:
    """
    Injects a timestamp into the filename

    :param filename: The filename to inject a timestamp into
    :return: The filename with a timestamp
    """
    basename, extension = split_filename(filename)
    date = return_timestamp()
    return f"{basename}_{date}{extension}"


def split_filename(filename: str) -> tuple[str, str]:
    """
    Split a filename into its base name and extension if it exists

    :param filename: The filename to split
    :return: A tuple of (basename, extension)
    """
    if "." in filename:
        basename, extension = filename.split(".", 1)
        extension = f".{extension}"
    else:
        basename, extension = filename, ""
    return basename, extension


def hash_file(file_path: str) -> str:
    """
    Hash a file using SHA256, for performance reasons, it reads the file in 4KB chunks in binary mode

    :param file_path: The path to the file to hash
    :return: The SHA256 hash of the file
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    return file_hash


@contextmanager
def tmp_local_dir(tmp_dir: str, cleanup: bool = True):
    """
    Create a temporary local directory for the pipeline

    :param tmp_dir: The directory to create the temporary local directory in
    :return: The temporary local directory
    """
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        yield tmp_dir
    finally:
        if cleanup:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
        else:
            print(f"Skipping {os.path.abspath(tmp_dir)} cleanup")


def return_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")
