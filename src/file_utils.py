import os
from contextlib import contextmanager
import shutil
from datetime import datetime
import hashlib

def create_local_path(path: str, filename: str) -> str:
    """
    Create the local path for a filename

    :param path: The path to create the local path for
    :param filename: The filename to create the local path for
    :return: The local path for the filename
    """
    return os.path.join(path, filename)

def get_filename(path: str) -> str:
    """
    Get the filename from a path

    :param path: The path to get the filename from
    :return: The filename
    """
    return os.path.basename(path)

def create_filename_with_timestamp(basename: str) -> str:
    """
    Create a filename with a timestamp

    :param basename: The basename of the file
    :return: The filename with a timestamp
    """
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{basename}_{date}.csv.gz"

def hash_file(file_path: str) -> str:
    """
    Hash a file using SHA256, for performance reasons, it reads the file in 4MB chunks in binary mode

    :param file_path: The path to the file to hash
    :return: The SHA256 hash of the file
    """
    print(f"Hashing file: {file_path}")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    print(f"Hash: {file_hash}")
    return file_hash

@contextmanager
def tmp_local_dir(tmp_dir: str):
    """
    Create a temporary local directory for the pipeline

    :param tmp_dir: The directory to create the temporary local directory in
    :return: The temporary local directory
    """
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        yield tmp_dir
    finally:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
