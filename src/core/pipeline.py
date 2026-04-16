from .config import Config
from src.storage import S3CatalogManager
from src.ingestion import CSVDownloader
from src.ingestion import LdrawDownloader
import logging
from src.messaging import SQSHandler
from botocore.exceptions import ClientError

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
        self.sqs_handler = SQSHandler(self.config.SQS_QUEUE_URL)

    def run(self):
        logger.info("Starting catalog pipeline run")

        self.prepare_csvs()
        self.prepare_ldraw()

        self.s3_manager.upload_manifest()

        sync_state = self.s3_manager.get_sync_state()

        self._reconcile(sync_state)

    def prepare_csvs(self):
        """
        Downloads CSVs and syncs them to S3 if they have changed.
        """
        downloads = self.csv_downloader.fetch_data()
        for resource, data in downloads.items():
            if self.s3_manager.check_for_resource_changes(resource, data["hash"]):
                logger.info(f"Changes detected for {resource}, uploading to S3")
                self._sync_resource(resource, data)
            else:
                logger.info(f"No change detected for {resource}")

    def prepare_ldraw(self):
        """
        Downloads LDraw library and syncs it to S3 if it has changed.
        """
        latest_ldraw_date = self.ldraw_downloader.get_latest_version_date()
        if self.s3_manager.check_for_ldraw_changes(latest_ldraw_date):
            logger.info("New LDraw library detected, downloading and uploading to S3")
            local_ldraw = self.ldraw_downloader.fetch_library()
            self._sync_ldraw(local_ldraw, latest_ldraw_date)

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
        print("AVAILABLE IDS  FROM CREATEINDEX", available_ids)
        self.s3_manager.update_manifest_ldraw_index(available_ids)

        logger.info("Uploading LDraw library to S3")
        s3_key = "ldraw.zip"
        if self.s3_manager.upload_to_s3(local_ldraw, s3_key):
            self.s3_manager.update_manifest_ldraw(s3_key, remote_date)
            logger.info("LDraw library synced successfully")

    def _convert_parts(self, part_ids: set[str]):
        """
        Sends part conversion jobs to SQS.
        """
        logger.info(f"Sending {len(part_ids)} part conversion jobs to SQS")
        for part_id in part_ids:
            try:
                self.sqs_handler.send_message("part_id", str(part_id))
            except ClientError as e:
                logger.error(f"S3 error removing file: {e}")
            except Exception as e:
                logger.error(f"Error removing file: {e}")
        logger.info("Part conversion jobs sent successfully")

    def _reconcile(self, sync_state: dict):
        """
        Reconciles the sync state.
        - Deduce orphan glbs (glbs that no longer exist in the csvs)
        - Send part conversion jobs to SQS for new parts.
        """
        orphan_glbs = sync_state["glb_state"] - sync_state["csv_state"]
        self.cleanup_orphan_glbs(orphan_glbs)

        if sync_state["to_convert_state"]:
            self._convert_parts(sync_state["to_convert_state"])

    def cleanup_orphan_glbs(self, orphan_glbs: set[str]):
        """
        Cleans up orphan glbs.
        """
        self.s3_manager.cleanup_orphan_glbs(orphan_glbs)
