from unittest.mock import MagicMock, patch
from src.ingestion.ldraw_downloader import LdrawDownloader
from urllib.request import Request
import pytest


@pytest.fixture
def manager():
    url = "http://localhost:8000"
    tmp_dir = "tmp"
    return LdrawDownloader(url, tmp_dir)


class TestGetLatestVersionDate:
    @patch("src.ingestion.ldraw_downloader.urlopen")
    def test_get_latest_version_date(self, mock_urlopen, manager):
        mock_response = MagicMock()
        mock_response.headers = {"Last-Modified": "Fri, 10 Apr 2026 12:06:19 GMT"}
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = manager.get_latest_version_date()

        assert result == "Fri, 10 Apr 2026 12:06:19 GMT"
        mock_urlopen.assert_called_once()
        actual_request = mock_urlopen.call_args[0][0]

        assert isinstance(actual_request, Request)
        assert actual_request.full_url == manager.library_url
        assert actual_request.get_method() == "HEAD"

    @patch("src.ingestion.ldraw_downloader.urlopen")
    def test_get_latest_version_date_missing_header(
        self, mock_urlopen, manager, caplog
    ):
        mock_response = MagicMock()
        mock_response.headers = {}
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = manager.get_latest_version_date()

        assert result is None
        assert "Unexpected error for get_latest_version_date" in caplog.text
