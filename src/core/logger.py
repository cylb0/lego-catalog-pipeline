import logging
import sys
import os


def setup_logging(filename: str = None, level: int = logging.INFO):
    """
    Setup logging configuration.
    If filename is provided, logs to file. Otherwise, logs to stdout.
    :param filename: The path to the log file (default: None)
    :param level: Logging level (default: logging.INFO)
    """
    config_params = {
        "level": level,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    }

    if filename:
        log_dir = os.path.dirname(filename)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        config_params["filename"] = filename
        config_params["filemode"] = "a"
    else:
        config_params["stream"] = sys.stdout

    logging.basicConfig(**config_params)
