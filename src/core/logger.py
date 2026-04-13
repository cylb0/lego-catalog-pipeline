import logging
import sys


def setup_logging(level=logging.INFO):
    """
    Setup logging configuration, stream to stdout for lambda logs
    :param level: Logging level (default: logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
