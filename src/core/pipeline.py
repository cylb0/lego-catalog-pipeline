from .config import Config
from src.storage import S3CatalogManager
from src.ingestion import CSVDownloader
from src.ingestion import LdrawDownloader
import logging
import json

logger = logging.getLogger(__name__)


class CatalogPipeline:
    """
    Orchestrates the catalog pipeline.
    """

    def __init__(self, config: Config):
        self.config = config
        self.s3_manager = S3CatalogManager(
            self.config.S3_BUCKET, self.config.MANIFEST_PATH, self.config.TMP_DIR
        )
        self.csv_downloader = CSVDownloader(self.config.RESOURCES, self.config.TMP_DIR)
        self.ldraw_downloader = LdrawDownloader(
            self.config.LDRAW_URL, self.config.TMP_DIR
        )

    def run(self):
        logger.info("Starting catalog pipeline run")

        downloads = self.csv_downloader.fetch_data()
        for resource, data in downloads.items():
            if self.s3_manager.check_for_resource_changes(resource, data["hash"]):
                logger.info(f"Changes detected for {resource}, uploading to S3")
                self._sync_resource(resource, data)
            else:
                logger.info(f"No change detected for {resource}")

        latest_ldraw_date = self.ldraw_downloader.get_latest_version_date()
        if self.s3_manager.check_for_ldraw_changes(latest_ldraw_date):
            logger.info("New LDraw library detected, downloading and uploading to S3")
            local_ldraw = self.ldraw_downloader.fetch_library()
            self._sync_ldraw(local_ldraw, latest_ldraw_date)

        logger.info(
            "Manifest before upload: \n%s",
            json.dumps(self.s3_manager.manifest.data, indent=4),
        )
        self.s3_manager.upload_manifest()

        sync_state = self.s3_manager.get_sync_state()

        self.s3_manager.cleanup_orphan_glbs(sync_state["csv_state"])

        if sync_state["to_convert_state"]:
            self._convert_parts(sync_state["to_convert_state"])

    def _sync_resource(self, resource: str, data: dict):
        """
        Sync a resource to S3.
        """
        old_filename = self.s3_manager.get_csv_filename(resource)

        if self.s3_manager.upload_to_s3(data["local_path"], data["filename"]):
            if old_filename and old_filename != data["filename"]:
                self.s3_manager.remove_from_s3(old_filename)
            self.s3_manager.update_manifest_resource(
                resource, data["filename"], data["hash"]
            )
        logger.info(f"Resource {resource} synced successfully")

    def _sync_ldraw(self, local_ldraw: str, remote_date: str):
        """
        Sync LDraw library to S3.
        """
        logger.info("Creating LDraw index...")
        available_ids = self.ldraw_downloader.create_index(local_ldraw)
        self.s3_manager.update_manifest_ldraw_index(available_ids)

        logger.info("Uploading LDraw library to S3")
        s3_key = "ldraw.zip"
        if self.s3_manager.upload_to_s3(local_ldraw, s3_key):
            self.s3_manager.update_manifest_ldraw(s3_key, remote_date)
            logger.info("LDraw library synced successfully")

    def _convert_parts(self, part_ids: set[str]):
        pass
