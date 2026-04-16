import boto3
import json
import logging

logger = logging.getLogger(__name__)


class SQSHandler:
    def __init__(self, queue_url: str):
        self.client = boto3.client("sqs")
        self.queue_url = queue_url

    def send_message(self, key: str, value: str):
        message = {"key": key, "value": value}
        try:
            self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
            )
            logger.info(f"Message sent to SQS: {message}")
        except Exception as e:
            logger.error(f"Error sending message to SQS: {e}")
