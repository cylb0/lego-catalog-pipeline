from src.core.config import Config, settings
from src.storage.s3_manager import S3CatalogManager
from src.ingestion.csv_downloader import CSVDownloader
from src.ingestion.ldraw_manager import LdrawManager
from src.core.file_utils import tmp_local_dir
import json
from src.core.logger import setup_logging
import logging

logger = logging.getLogger(__name__)


def sync_resource(resource: str, data: dict, s3_manager: S3CatalogManager):
    if not s3_manager.check_for_resource_changes(resource, data["hash"]):
        logger.info(f"No changes detected for {resource}")
        return

    logger.info(f"Changes detected for {resource}, uploading to S3")
    old_filename = s3_manager.get_csv_filename(resource)

    if s3_manager.upload_to_s3(data["local_path"], data["filename"]):
        if old_filename and old_filename != data["filename"]:
            s3_manager.remove_from_s3(old_filename)
        s3_manager.update_manifest_resource(resource, data["filename"], data["hash"])
    logger.info(f"Resource {resource} synced successfully")


def sync_ldraw(local_ldraw: str, remote_date: str, s3_manager: S3CatalogManager):
    if not s3_manager.check_for_ldraw_changes(remote_date):
        logger.info("No changes detected for LDraw library")
        return

    logger.info("Changes detected for LDraw library, uploading to S3")
    s3_key = "ldraw.zip"
    s3_manager.upload_to_s3(local_ldraw, s3_key)
    s3_manager.update_manifest_ldraw(s3_key, remote_date)
    logger.info("LDraw library synced successfully")


def main(config: Config):
    setup_logging()

    with tmp_local_dir(config.TMP_DIR):
        s3_manager = S3CatalogManager(
            config.S3_BUCKET, config.MANIFEST_PATH, config.TMP_DIR
        )
        csv_downloader = CSVDownloader(config.RESOURCES, config.TMP_DIR)
        ldraw_manager = LdrawManager(config.LDRAW_URL, config.TMP_DIR)

        downloads = csv_downloader.fetch_data()

        for resource, data in downloads.items():
            sync_resource(resource, data, s3_manager)

        latest_ldraw_date = ldraw_manager.get_latest_version_date()

        if s3_manager.check_for_ldraw_changes(latest_ldraw_date):
            logger.info("New LDraw library detected, downloading and uploading to S3")
            local_ldraw = ldraw_manager.fetch_library()
            sync_ldraw(local_ldraw, latest_ldraw_date, s3_manager)

        logger.info(
            "Manifest before upload: \n%s",
            json.dumps(s3_manager.manifest.data, indent=4),
        )
        s3_manager.upload_manifest()


if __name__ == "__main__":
    main(settings)
