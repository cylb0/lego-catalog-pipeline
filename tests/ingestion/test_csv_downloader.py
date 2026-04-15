from unittest.mock import patch
import pytest
from src.ingestion import CSVDownloader


@pytest.fixture
def downloader():
    resources = {
        "parts": "https://example.com/data.csv",
        "categories": "https://example.com/data.csv",
    }
    tmp_dir = "tmp"
    return CSVDownloader(resources, tmp_dir)


@patch("src.ingestion.csv_downloader.urlretrieve")
def test_download_file_success(mock_urlretrieve, downloader):
    result = downloader.download_file("https://example.com/data.csv", "/tmp/data.csv")

    mock_urlretrieve.assert_called_once_with(
        "https://example.com/data.csv", "/tmp/data.csv"
    )
    assert result == "/tmp/data.csv"


class TestFetchResource:
    @patch("src.ingestion.csv_downloader.create_filename_with_timestamp")
    @patch("src.ingestion.csv_downloader.join_path")
    def test_fetch_resources_calls_download_file_with_correct_path_success(
        self, mock_join_path, mock_filename, downloader
    ):
        local_path = "/tmp/test.csv"
        mock_filename.return_value = "test.csv"
        mock_join_path.return_value = local_path

        with patch.object(
            downloader, "download_file", return_value=local_path
        ) as mock_download_file:
            result = downloader.fetch_resource("parts")
            assert result == local_path
            mock_download_file.assert_called_once_with(
                downloader.resources["parts"], local_path
            )

    def test_fetch_resources_call_with_non_existent_resource_fails(self, downloader):
        result = downloader.fetch_resource("non_existent")

        assert result is None
