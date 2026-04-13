from src.core.config import Config, settings
from src.core.file_utils import tmp_local_dir
from src.core.logger import setup_logging
from src.core.pipeline import CatalogPipeline
import logging
import os

logger = logging.getLogger(__name__)

is_lambda = "AWS_LAMBDA_FUNCTION_NAME" in os.environ


def main(config: Config):
    setup_logging(filename=config.LOG_FILE if not is_lambda else None)

    with tmp_local_dir(config.TMP_DIR):
        pipeline = CatalogPipeline(config)
        pipeline.run()


if __name__ == "__main__":
    main(settings)
