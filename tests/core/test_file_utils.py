from src.core.utils import (
    split_filename,
    create_filename_with_timestamp,
    hash_file,
    tmp_local_dir,
)
from unittest.mock import patch
from datetime import datetime
import hashlib
import os


class TestSplitFilename:
    def test_split_filename_with_extension(self):
        filename = "parts.csv"
        basename, extension = split_filename(filename)

        assert basename == "parts"
        assert extension == ".csv"

    def test_split_filename_with_complex_extension(self):
        filename = "parts.tar.gz"
        basename, extension = split_filename(filename)

        assert basename == "parts"
        assert extension == ".tar.gz"

    def test_split_filename_without_extension(self):
        filename = "parts"
        basename, extension = split_filename(filename)

        assert basename == "parts"
        assert extension == ""


class TestCreateFileNameWithTimeStamp:
    time = datetime(2026, 4, 10, 11, 40, 55)

    @patch("src.core.utils.file_utils.datetime")
    def test_create_filename_with_timestamp_returns_filename_with_timestamp_and_extension(
        self, mock_datetime
    ):
        mock_datetime.now.return_value = self.time

        filename = create_filename_with_timestamp("parts.csv")

        assert filename == "parts_20260410114055.csv"

    @patch("src.core.utils.file_utils.datetime")
    def test_create_filename_with_timestamp_returns_filename_with_timestamp_no_extension(
        self, mock_datetime
    ):
        mock_datetime.now.return_value = self.time

        filename = create_filename_with_timestamp("parts")

        assert filename == "parts_20260410114055"


class TestHashFile:
    def test_hash_file_returns_correct_sha256_hash(self, tmp_path):
        dummy_file = tmp_path / "dummy.txt"
        content = b"hello world"
        dummy_file.write_bytes(content)

        expected_hash = hashlib.sha256(content).hexdigest()

        result = hash_file(str(dummy_file))

        assert result == expected_hash
        assert len(result) == 64

    def test_hash_file_empty_file(self, tmp_path):
        dummy_file = tmp_path / "dummy.txt"
        dummy_file.write_bytes(b"")

        expected_hash = hashlib.sha256(b"").hexdigest()

        result = hash_file(str(dummy_file))

        assert result == expected_hash

    def test_hash_file_loops_through_large_files(self, tmp_path):
        dummy_file = tmp_path / "dummy.txt"
        content = b"hello world" * 10000
        dummy_file.write_bytes(content)

        expected_hash = hashlib.sha256(content).hexdigest()

        result = hash_file(str(dummy_file))

        assert result == expected_hash


class TestTmpLocalDir:
    def test_tmp_local_dir_creates_and_cleansup(self, tmp_path):
        test_dir = str(tmp_path / "test_dir")

        assert not os.path.exists(test_dir)

        with tmp_local_dir(test_dir) as path:
            assert path == test_dir
            assert os.path.isdir(test_dir)

            with open(os.path.join(test_dir, "test.txt"), "w") as f:
                f.write("test")

        assert not os.path.exists(test_dir)

    def test_tmp_local_dir_cleanup_on_failure(self, tmp_path):
        test_dir = str(tmp_path / "test_dir")

        assert not os.path.exists(test_dir)

        try:
            with tmp_local_dir(test_dir) as path:
                assert os.path.exists(test_dir)

                raise Exception("test")
        except Exception:
            pass

        assert not os.path.exists(test_dir)
