from functools import wraps
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from src.file_utils import join_path, get_filename, create_filename_with_timestamp, hash_file
import os

class CSVDownloader:
    def __init__(self, resources: dict[str, str], tmp_dir: str):
        """
        Initialize the CSVDownloader

        :param resources: The resources to download
        :param tmp_dir: The directory to download the resources to
        """
        self.resources: dict[str, str] = resources
        self.tmp_dir: str = tmp_dir
    
    def handle_download_errors(func):
        """
        Wrapper to handle download errors

        :param func: The function to wrap
        :return: The result of the function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            label = kwargs.get("label", func.__name__)
            try:
                return func(*args, **kwargs)
            except HTTPError as e:
                print(f"HTTP Error for {label}: {e.code} - {e.reason}")
            except URLError as e:
                print(f"URL Error for {label}: {e.reason}")
            except OSError as e:
                print(f"OS Error for {label}: {e.strerror}")
            except Exception as e:
                print(f"Unexpected error for {label}: {e}")
            return None
        return wrapper

    def fetch_resource(self, resource: str) -> str | None:
        """
        Fetches a single csv file from a given url

        :param resource: The name of the resource (e.g., "parts")
        :return: The path to the downloaded file or None if the download failed
        """
        url = self.resources.get(resource)

        if not url:
            print(f"Resource {resource} not found")
            return None

        original_filename = os.path.basename(url)
        timestamped_filename = create_filename_with_timestamp(original_filename)
        local_path = join_path(self.tmp_dir, timestamped_filename)

        return self.download_file(url, local_path)

    @handle_download_errors
    def download_file(self, url: str, path: str) -> str:
        """
        Downloads a file from a given url to a given path

        :param url: The url to download the file from
        :param path: The path to download the file to
        :return: The path to the downloaded file
        """
        print(f"Downloading {url}...")
        urlretrieve(url, path)
        print(f"Downloaded in {path}")
        return path

    def fetch_data(self) -> dict[str, dict[str, str]]:
        results = {}
        for resource, url in self.resources.items():
            local_path = self.fetch_resource(resource)
            if local_path:
                results[resource] = {
                    "local_path": local_path,
                    "filename": get_filename(local_path),
                    "hash": hash_file(local_path),
                }
        return results
