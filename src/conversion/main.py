import logging
import dotenv
import os

from src.messaging.sqs_handler import SQSHandler
from src.conversion.s3_client import S3Client
from src.conversion.worker import poll_and_process, prepare_ldraw

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run():
    dotenv.load_dotenv()

    logger.info("[CONVERSION] Conversion worker starting")

    sqs = SQSHandler(os.getenv("SQS_QUEUE_URL"))
    s3 = S3Client(os.getenv("S3_BUCKET_NAME"))

    zip_path = os.getenv("LDRAW_PATH", "/tmp/ldraw.zip")
    extract_path = "/tmp/ldraw"
    output_path = os.getenv("OUTPUT_PATH", "/tmp/output")
    max_empty_polls = int(os.getenv("MAX_EMPTY_POLLS", 3))

    ldraw_dir = prepare_ldraw(s3, "ldraw.zip", zip_path, extract_path)

    if not ldraw_dir:
        logger.error("[CONVERSION] Failed to download ldraw archive. Aborting.")
        return

    poll_and_process(sqs, s3, ldraw_dir, output_path, max_empty_polls)

    logger.info("[CONVERSION] Conversion run complete")


if __name__ == "__main__":
    run()
