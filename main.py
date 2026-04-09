from src.config import Config, settings
from src.s3_manager import S3CatalogManager
from src.csv_downloader import CSVDownloader
from src.file_utils import tmp_local_dir

def main(config: Config):
    with tmp_local_dir(config.TMP_DIR) as tmp_dir:
        s3_manager = S3CatalogManager(config.S3_BUCKET, config.MANIFEST_PATH, config.TMP_DIR)
        downloader = CSVDownloader(config.RESOURCES, config.TMP_DIR)

        downloads = downloader.fetch_data()

        for resource, data in downloads.items():
            if s3_manager.check_for_changes(resource, data["hash"]):
                print(f"Changes detected for {resource}, uploading to S3")
                old_filename = s3_manager.manifest.get(resource, {}).get("filename")
                s3_manager.upload_to_s3(data["local_path"], data["filename"])
                if old_filename and old_filename != data["filename"]:
                    s3_manager.remove_from_s3(old_filename)
                s3_manager.update_manifest(resource, data["filename"], data["hash"])

        s3_manager.upload_manifest()

if __name__ == "__main__":
    main(settings)
