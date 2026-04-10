from unittest.mock import patch, MagicMock
import pytest
from src.csv_downloader import CSVDownloader
from urllib.error import HTTPError, URLError

@pytest.fixture
def downloader():
    resources = {
        "parts": "https://example.com/data.csv",
        "categories": "https://example.com/data.csv",
    }
    tmp_dir = "tmp"
    return CSVDownloader(resources, tmp_dir)

class TestDownloadFileDecorator:
    URL = "https://example.com/data.csv"
    PATH = "/tmp/data.csv"

    @patch("src.csv_downloader.urlretrieve")
    def test_download_file_success(self, mock_urlretrieve, downloader):
        result = downloader.download_file(self.URL, self.PATH)

        mock_urlretrieve.assert_called_once_with(self.URL, self.PATH)
        assert result == self.PATH

    @patch("src.csv_downloader.urlretrieve")
    def test_download_file_network_error(self, mock_urlretrieve, downloader):
        mock_urlretrieve.side_effect = HTTPError("Error", 404, "Not Found", {}, None)

        result = downloader.download_file(self.URL, self.PATH)

        assert result is None

    @patch("src.csv_downloader.urlretrieve")
    def test_download_file_url_error(self, mock_urlretrieve, downloader):
        mock_urlretrieve.side_effect = URLError("Error")

        result = downloader.download_file(self.URL, self.PATH)

        assert result is None

    @patch("src.csv_downloader.urlretrieve")
    def test_download_file_os_error(self, mock_urlretrieve, downloader):
        mock_urlretrieve.side_effect = OSError()

        result = downloader.download_file(self.URL, self.PATH)
        
        assert result is None

    @patch("src.csv_downloader.urlretrieve")
    def test_download_file_exception(self, mock_urlretrieve, downloader):
        mock_urlretrieve.side_effect = Exception()

        result = downloader.download_file(self.URL, self.PATH)
        
        assert result is None
