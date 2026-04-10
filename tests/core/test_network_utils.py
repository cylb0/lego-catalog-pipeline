from src.core.network_utils import handle_download_errors

@handle_download_errors
def mock_download(url, path):
    if "https" in url:
        return path
    elif "http" in url:
        raise HTTPError("Error", 404, "Not Found", {}, None)
    elif "url" in url:
        raise URLError("Error")
    elif "os" in url:
        raise OSError("Error")
    elif "exception" in url:
        raise Exception("Error")

def test_handle_download_errors_success():
    assert mock_download("https://example.com/data.csv", "/tmp/data.csv") == "/tmp/data.csv"

def test_handle_download_errors_http_error():
    assert mock_download("http://example.com/data.csv", "/tmp/data.csv") is None

def test_handle_download_errors_url_error():
    assert mock_download("url://example.com/data.csv", "/tmp/data.csv") is None

def test_handle_download_errors_os_error():
    assert mock_download("os://example.com/data.csv", "/tmp/data.csv") is None

def test_handle_download_errors_exception():
    assert mock_download("exception://example.com/data.csv", "/tmp/data.csv") is None