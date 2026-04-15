from src.core.utils import join_path, handle_download_errors
from urllib.request import urlretrieve, Request, urlopen
import logging
import zipfile
import os

logger = logging.getLogger(__name__)


class LdrawDownloader:
    def __init__(self, library_url: str, tmp_dir: str):
        self.library_url = library_url
        self.tmp_dir = tmp_dir

    @handle_download_errors
    def fetch_library(self):
        logger.info(f"Downloading ldraw library from {self.library_url}...")
        local_path = urlretrieve(self.library_url, join_path(self.tmp_dir, "ldraw.zip"))
        logger.info(f"Ldraw library downloaded successfully to {local_path[0]}")
        return local_path[0]

    @handle_download_errors
    def get_latest_version_date(self):
        logger.info("Getting latest version date...")
        req = Request(self.library_url, method="HEAD")
        with urlopen(req) as response:
            date = response.headers["Last-Modified"]
            logger.info(f"Latest version date: {date}")
            return date

    def create_index(self, local_ldraw: str) -> set[str]:
        print("local_ldraw", local_ldraw)
        """
        Creates an index containing every available part within ldraw archive.
        :return: A set containing every part id
        """
        available_ids = set()
        logger.info(f"Indexing Ldraw library at {local_ldraw}...")

        with zipfile.ZipFile(local_ldraw, "r") as z:
            for filepath in z.namelist():
                if "complete/ldraw/parts" in filepath and filepath.endswith(".dat"):
                    if "/s/" not in filepath:
                        filename = os.path.basename(filepath)
                        part_id = filename.lower().replace(".dat", "")
                        available_ids.add(part_id)
        return available_ids
