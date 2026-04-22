import boto3
import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SQSHandler:
    def __init__(self, queue_url: str):
        self.client = boto3.client("sqs")
        self.queue_url = queue_url

    def send_message(self, key: str, value: str):
        message = {key: value}
        try:
            self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
            )
            logger.info(f"[SQS] Message sent to SQS: {message}")
        except Exception as e:
            logger.error(f"[SQS] Error sending message to SQS: {e}")

    def receive_messages(self, max_messages=10, wait_time=20):
        try:
            response = self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
            )
            return response.get("Messages", [])
        except ClientError as e:
            logger.error("[SQS] Error while receiving messages from SQS: %s", e)
            return []
        except Exception as e:
            logger.error("[SQS] Error while receiving messages from SQS: %s", e)
            return []

    def delete_message(self, receipt_handle: str):
        try:
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
            logger.info(f"[SQS] Deleted message with receipt handle: {receipt_handle}")
            return True
        except ClientError as e:
            logger.error("[SQS] Error while deleting SQS message", e)
            return False
        except Exception as e:
            logger.error("[SQS] Error while deleting message", e)
            return False
