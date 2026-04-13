from src.core.config import Config, settings
from src.storage.s3_manager import S3CatalogManager
from src.ingestion.csv_downloader import CSVDownloader
from src.ingestion.ldraw_manager import LdrawManager
from src.core.file_utils import tmp_local_dir
import json


def sync_resource(resource: str, data: dict, s3_manager: S3CatalogManager):
    if not s3_manager.check_for_resource_changes(resource, data["hash"]):
        return

    print(f"Changes detected for {resource}, uploading to S3")
    old_filename = s3_manager.get_csv_filename(resource)

    if s3_manager.upload_to_s3(data["local_path"], data["filename"]):
        if old_filename and old_filename != data["filename"]:
            s3_manager.remove_from_s3(old_filename)
        s3_manager.update_manifest_resource(resource, data["filename"], data["hash"])


def sync_ldraw(local_ldraw: str, remote_date: str, s3_manager: S3CatalogManager):
    s3_key = "ldraw.zip"
    s3_manager.upload_to_s3(local_ldraw, s3_key)
    s3_manager.update_manifest_ldraw(s3_key, remote_date)


def main(config: Config):
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
            print("New LDraw library detected, downloading and uploading to S3")
            local_ldraw = ldraw_manager.fetch_library()
            sync_ldraw(local_ldraw, latest_ldraw_date, s3_manager)

        print(
            "Manifest before upload: ", json.dumps(s3_manager.manifest.data, indent=4)
        )
        s3_manager.upload_manifest()


if __name__ == "__main__":
    main(settings)
