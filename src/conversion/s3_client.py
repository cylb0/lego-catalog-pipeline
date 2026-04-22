import boto3
import logging

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self, bucket: str):
        self.client = boto3.client("s3")
        self.bucket = bucket

    def download_file(self, key: str, local_path: str):
        logger.info(f"Downloading s3://{self.bucket}/{key} -> {local_path}")
        self.client.download_file(self.bucket, key, local_path)
        logger.info(f"Downloaded s3://{self.bucket}/{key} -> {local_path}")

    def upload_file(self, local_path: str, key: str):
        logger.info(f"Uploading s3://{self.bucket}/{key} <- {local_path}")
        self.client.upload_file(local_path, self.bucket, key)
        logger.info(f"Uploaded s3://{self.bucket}/{key} <- {local_path}")
