import logging
import watchtower
import sys
import os
import boto3


def setup_logging(
    filename: str = None, level: int = logging.INFO, cloud_group: str = None
):
    """
    Configure logging for the application. It will either log to a file, stdout and AWS CloudWatch.

    :param filename: The path to the log file (default: None)
    :param level: Logging level (default: logging.INFO)
    :param cloud_group: The CloudWatch log group (default: None)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if cloud_group:
        logs_client = boto3.client("logs", region_name="eu-west-3")
        cw_handler = watchtower.CloudWatchLogHandler(
            log_group=cloud_group, boto3_client=logs_client, send_interval=5
        )
        cw_handler.setFormatter(formatter)
        root_logger.addHandler(cw_handler)

    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        file_handler = logging.FileHandler(filename, mode="a")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # config_params = {
    #     "level": level,
    #     "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # }

    # if filename:
    #     log_dir = os.path.dirname(filename)
    #     if log_dir:
    #         os.makedirs(log_dir, exist_ok=True)
    #     config_params["filename"] = filename
    #     config_params["filemode"] = "a"
    # else:
    #     config_params["stream"] = sys.stdout

    # logging.basicConfig(**config_params)
