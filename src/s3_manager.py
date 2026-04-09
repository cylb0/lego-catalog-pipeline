import boto3
from botocore.exceptions import ClientError
import os
import json

class S3CatalogManager:
    def __init__(self, bucket: str, manifest_key: str, tmp_dir: str):
        """
        Initialize the S3CatalogManager and retrieves the manifest file from S3 if it exists

        :param bucket: The S3 bucket name
        :param manifest_key: The key of the manifest file in S3
        :param tmp_dir: The directory to download the manifest to
        """
        self.client = boto3.client('s3')
        self.bucket: str = bucket
        self.manifest_key: str = manifest_key
        self.tmp_dir: str = tmp_dir
        self.local_manifest_path: str = os.path.join(tmp_dir, manifest_key)
        self.manifest: dict[str, dict[str, str]] = self._fetch_manifest()
        self.manifest_changed: bool = False

    def _fetch_manifest(self):
        """
        Fetch the manifest file from S3

        :return: The manifest file or an empty dictionary if it doesn't exist
        """
        try:
            self.client.download_file(self.bucket, self.manifest_key, self.local_manifest_path)
            with open(self.local_manifest_path, 'r') as f:
                return json.load(f)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
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

    def upload_to_s3(self, path: str, filename: str) -> bool:
        """
        Upload a file to S3

        :param path: The path to the file to upload
        :param filename: The name of the file to upload
        :return: True if the file was uploaded successfully, False otherwise
        """
        try:
            self.client.upload_file(path, self.bucket, filename)
            print(f"Uploaded {path} to s3://{self.bucket}/{filename}")
            return True
        except ClientError as e:
            print(f"S3 error uploading file: {e}")
            return False

    def remove_from_s3(self, filename: str) -> bool:
        """
        Remove a file from S3

        :param filename: The filename to remove
        :return: True if the file was removed successfully, False otherwise
        """
        if filename in self.manifest and "filename" in self.manifest[filename]:
            filename = self.manifest[resource]["filename"]
            try:
                self.client.delete_object(self.bucket, filename)
                print(f"Removed {filename} from s3://{self.bucket}")
                return True
            except ClientError as e:
                print(f"S3 error removing file: {e}")
                return False

    def check_for_changes(self, resource: str, hash: str) -> bool:
        """
        Check for differences between manifest and new resource

        :param resource: The resource to check
        :param hash: The hash of the new resource
        :return: True if the resource has changed, False otherwise
        """
        return self.manifest.get(resource, {}).get("hash") != hash

    def update_manifest(self, resource: str, filename: str, hash: str) -> bool:
        """
        Update the manifest with the new resource

        :param resource: The resource to update
        :param filename: The name of the file to update
        :param hash: The hash of the file
        :return: True if the manifest was updated successfully, False otherwise
        """
        self.manifest[resource] = {"filename": filename, "hash": hash}
        try:
            with open(self.local_manifest_path, 'w') as f:
                json.dump(self.manifest, f)
            self.upload_to_s3(self.local_manifest_path, self.manifest_key)
            self.manifest_changed = True
            return True
        except (IOError, ClientError) as e:
            print(f"Error updating manifest: {e}")
            return False

    def upload_manifest(self) -> bool:
        """
        Upload the manifest to S3 if it has changed

        :return: True if the manifest was uploaded successfully or if there were no changes, False otherwise
        """
        if not self.manifest_changed:
            print(f"No changes detected in manifest, skipping upload")
            return True

        print(f"Uploading manifest to s3://{self.bucket}/{self.manifest_key}")
        success = self.upload_to_s3(self.local_manifest_path, self.manifest_key)
        
        if success:
            self.manifest_changed = False
            
        return success