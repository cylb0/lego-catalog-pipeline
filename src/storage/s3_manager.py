import boto3
from botocore.exceptions import ClientError
import os
import json
from src.core.file_utils import return_timestamp
from src.core.catalog_manifest import CatalogManifest


class S3CatalogManager:
    def __init__(self, bucket: str, manifest_key: str, tmp_dir: str):
        """
        Initialize the S3CatalogManager and retrieves the manifest file from S3 if it exists

        :param bucket: The S3 bucket name
        :param manifest_key: The key of the manifest file in S3
        :param tmp_dir: The directory to download the manifest to
        """
        self.client = boto3.client("s3")
        self.bucket: str = bucket
        self.manifest_key: str = manifest_key
        self.tmp_dir: str = tmp_dir
        self.local_manifest_path: str = os.path.join(tmp_dir, manifest_key)
        raw_manifest = self._fetch_manifest()
        self.manifest = CatalogManifest(raw_manifest)

    def _fetch_manifest(self):
        """
        Fetch the manifest file from S3

        :return: The manifest file or an empty dictionary if it doesn't exist
        """
        try:
            self.client.download_file(
                self.bucket, self.manifest_key, self.local_manifest_path
            )
            with open(self.local_manifest_path, "r") as f:
                return json.load(f)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("No manifest found in S3, starting fresh.")
            else:
                print(f"S3 error fetching manifest: {e}")
            return {}
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading manifest: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error fetching manifest: {e}")
            return {}

    def _save_local_manifest(self) -> bool:
        """
        Save the manifest to a local file

        :return: True if the manifest was saved successfully, False otherwise
        """
        try:
            with open(self.local_manifest_path, "w") as f:
                json.dump(self.manifest.data, f)
            self.manifest.changed = True
            return True
        except IOError as e:
            print(f"Error updating manifest locally: {e}")
            return False

    def upload_to_s3(self, path: str, s3_key: str) -> bool:
        """
        Upload a file to S3

        :param path: The path to the file to upload
        :param s3_key: The S3 key of the file to upload
        :return: True if the file was uploaded successfully, False otherwise
        """
        try:
            self.client.upload_file(path, self.bucket, s3_key)
            print(f"Uploaded {path} to s3://{self.bucket}/{s3_key}")
            return True
        except FileNotFoundError as e:
            print(f"Local file not found: {path}")
            return False
        except ClientError as e:
            print(f"S3 error uploading file: {e}")
            return False

    def remove_from_s3(self, s3_key: str) -> bool:
        """
        Remove a file from S3

        :param s3_key: The S3 key of the file to remove
        :return: True if the file was removed successfully, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=s3_key)
            print(f"Removed {s3_key} from s3://{self.bucket}")
            return True
        except ClientError as e:
            print(f"S3 error removing file: {e}")
            return False

    def check_for_resource_changes(self, resource: str, hash: str) -> bool:
        """
        Check for differences between manifest and new resource

        :param resource: The resource to check
        :param hash: The hash of the new resource
        :return: True if the resource has changed, False otherwise
        """
        return self.manifest.check_csv_change(resource, hash)

    def update_manifest_resource(self, resource: str, filename: str, hash: str) -> bool:
        """
        Update the manifest with the new resource

        :param resource: The resource to update
        :param filename: The name of the file to update
        :param hash: The hash of the file
        :return: True if the manifest was updated successfully, False otherwise
        """
        self.manifest.update_csv_resource(resource, filename, hash)
        return self._save_local_manifest()

    def check_for_ldraw_changes(self, remote_date: str) -> bool:
        """
        Check for differences between manifest and new LDraw library

        :param remote_date: The last modified date of the remote file
        :return: True if the LDraw library has changed, False otherwise
        """
        return self.manifest.check_ldraw_change(remote_date)

    def update_manifest_ldraw(self, filename: str, remote_date: str) -> bool:
        """
        Update the manifest with the new LDraw library

        :param filename: The name of the file to update
        :param remote_date: The last modified date of the remote file
        :return: True if the manifest was updated successfully, False otherwise
        """
        self.manifest.update_ldraw(filename, remote_date)
        return self._save_local_manifest()

    def upload_manifest(self) -> bool:
        """
        Upload the manifest to S3 if it has changed

        :return: True if the manifest was uploaded successfully or if there were no changes, False otherwise
        """
        if not self.manifest.changed:
            print(f"No changes detected in manifest, skipping upload")
            return True

        print(f"Uploading manifest to s3://{self.bucket}/{self.manifest_key}")
        success = self.upload_to_s3(self.local_manifest_path, self.manifest_key)

        if success:
            self.manifest.changed = False

        return success
