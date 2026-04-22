from src.core.utils import join_path, handle_download_errors
from urllib.request import Request, urlopen
import logging
import zipfile
import os
import re

logger = logging.getLogger(__name__)


class LdrawDownloader:
    def __init__(self, webpage_url: str, library_url: str, tmp_dir: str):
        self.webpage_url = webpage_url
        self.library_url = library_url
        self.tmp_dir = tmp_dir

    @handle_download_errors
    def fetch_library(self):
        logger.info(f"Downloading ldraw library from {self.library_url}...")
        local_path = join_path(self.tmp_dir, "ldraw.zip")
        req = Request(self.library_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as response, open(local_path, "wb") as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)

        logger.info(f"Ldraw library downloaded successfully to {local_path}")
        return local_path

    @handle_download_errors
    def get_latest_version_date(self):
        logger.info("Getting latest version date...")
        req = Request(self.webpage_url, headers={"User-Agent": "Mozilla/5.0"})

        with urlopen(req) as response:
            html = response.read().decode("utf-8")

        match = re.search(r"LDraw\.org Parts Update (\d{4}-\d{2})", html)
        if match:
            return match.group(1)

    def create_index(self, local_ldraw: str) -> set[str]:
        """
        Creates an index containing every available part within ldraw archive.
        :return: A set containing every part id
        """
        available_ids = set()
        logger.info(f"Indexing Ldraw library at {local_ldraw}...")

        with zipfile.ZipFile(local_ldraw, "r") as z:
            for filepath in z.namelist():
                if "ldraw/parts" in filepath and filepath.endswith(".dat"):
                    if "/s/" not in filepath:
                        filename = os.path.basename(filepath)
                        part_id = filename.lower().replace(".dat", "")
                        available_ids.add(part_id)
        return available_ids
