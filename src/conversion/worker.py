import logging
import json
from src.messaging.sqs_handler import SQSHandler
from src.conversion.converter import convert_part
from src.conversion.s3_client import S3Client
from src.conversion.ldraw_unpacker import extract_ldraw_zip

logger = logging.getLogger(__name__)


def prepare_ldraw(s3: S3Client, key: str, local_path: str, extract_path: str) -> str:
    """
    Download ldraw.zip from S3 and extract it to a local directory.

    :param s3: S3 client
    :param key: S3 key for ldraw.zip
    :param local_path: Local path to save ldraw.zip
    :param extract_path: Local path to extract ldraw.zip
    :return: Path to extracted ldraw directory
    """
    s3.download_file(key, local_path)

    return extract_ldraw_zip(local_path, extract_path)


def process_messages(
    messages: list,
    sqs: SQSHandler,
    s3: S3Client,
    ldraw_dir: str,
    output_path: str,
):
    logger.info(f"Processing {len(messages)} messages")

    for message in messages:
        body = json.loads(message["Body"])
        part_id = body["part_id"]

        if convert_part(part_id, ldraw_dir, output_path):
            try:
                s3.upload_file(f"{output_path}/{part_id}.glb", f"glbs/{part_id}.glb")
                sqs.delete_message(message["ReceiptHandle"])
            except Exception as e:
                logger.error(f"Failed to upload part {part_id}: {e}")
        else:
            logger.warning(f"Conversion failed for part {part_id}")


def poll_and_process(
    sqs: SQSHandler,
    s3: S3Client,
    ldraw_dir: str,
    output_path: str,
    max_empty_polls: int,
):
    empty_polls = 0
    logger.info("Starting polling loop")

    while empty_polls < max_empty_polls:
        messages = sqs.receive_messages()

        if not messages:
            empty_polls += 1
            logger.info(f"No messages (empty poll {empty_polls}/{max_empty_polls})")
            continue

        empty_polls = 0

        logger.info(f"Processing {len(messages)} messages")
        process_messages(messages, sqs, s3, ldraw_dir, output_path)

    logger.info("No messages for a while -> stopping worker")
