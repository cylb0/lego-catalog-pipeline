from src.core.config import Config, settings
from src.core.file_utils import tmp_local_dir
from src.core.logger import setup_logging
from src.core.pipeline import CatalogPipeline


def main(config: Config):
    cw_group = config.CLOUDWATCH_LOG_GROUP if config.FORCE_CLOUD_LOGGING else None
    log_file = (
        config.LOG_FILE
        if (not config.IS_LAMBDA and not config.FORCE_CLOUD_LOGGING)
        else None
    )

    setup_logging(filename=log_file, cloud_group=cw_group)

    with tmp_local_dir(config.TMP_DIR):
        pipeline = CatalogPipeline(config)
        pipeline.run()


if __name__ == "__main__":
    main(settings)
