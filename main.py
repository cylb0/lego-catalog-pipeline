from src.config import Config, settings
from src.s3_manager import S3CatalogManager
from src.csv_downloader import CSVDownloader
from src.file_utils import tmp_local_dir

def sync_resource(resource: str, data: dict, s3_manager: S3CatalogManager):
    if not s3_manager.check_for_changes(resource, data["hash"]):
        return
    
    print(f"Changes detected for {resource}, uploading to S3")
    old_filename = s3_manager.manifest.get(resource, {}).get("filename")
    
    if s3_manager.upload_to_s3(data["local_path"], data["filename"]):
        if old_filename and old_filename != data["filename"]:
            s3_manager.remove_from_s3(old_filename)
        s3_manager.update_manifest(resource, data["filename"], data["hash"])

def main(config: Config):
    with tmp_local_dir(config.TMP_DIR) as tmp_dir:
        s3_manager = S3CatalogManager(config.S3_BUCKET, config.MANIFEST_PATH, config.TMP_DIR)
        downloader = CSVDownloader(config.RESOURCES, config.TMP_DIR)

        downloads = downloader.fetch_data()

        for resource, data in downloads.items():
            sync_resource(resource, data, s3_manager)

        s3_manager.upload_manifest()

if __name__ == "__main__":
    main(settings)
