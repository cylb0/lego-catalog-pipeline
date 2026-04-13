from src.core.file_utils import join_path
from urllib.request import urlretrieve, Request, urlopen
from src.core.network_utils import handle_download_errors
import logging

logger = logging.getLogger(__name__)


class LdrawManager:
    def __init__(self, library_url: str, tmp_dir: str):
        self.library_url = library_url
        self.tmp_dir = tmp_dir

    @handle_download_errors
    def fetch_library(self):
        logger.info(f"Downloading ldraw library from {self.library_url}...")
        local_path = urlretrieve(self.library_url, join_path(self.tmp_dir, "ldraw.zip"))
        logger.info(f"Ldraw library downloaded successfully to {local_path[0]}")
        return local_path[0]

    def get_latest_version_date(self):
        req = Request(self.library_url, method="HEAD")
        with urlopen(req) as response:
            date = response.headers["Last-Modified"]
            logger.info(f"Latest version date: {date}")
            return date
