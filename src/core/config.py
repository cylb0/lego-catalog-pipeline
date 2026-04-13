import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._init_env()
        return cls._instance

    def _init_env(self):
        self.S3_BUCKET: str = self._get_required_env("S3_BUCKET_NAME")
        self.MANIFEST_PATH: str = os.getenv("MANIFEST_PATH", "manifest.json")
        self.TMP_DIR: str = os.getenv("TMP_DIR", "tmp")

        self.RESOURCES: dict[str, str] = {
            "parts": self._get_required_env("REBRICKABLE_PARTS_CSV_URL"),
            "categories": self._get_required_env("REBRICKABLE_CATEGORIES_CSV_URL"),
        }

        self.LDRAW_URL = self._get_required_env("LDRAW_COMPLETE_LIBRARY_URL")
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/catalog_pipeline.log")
        self.CLOUDWATCH_LOG_GROUP = self._get_required_env("CLOUDWATCH_LOG_GROUP")
        self.FORCE_CLOUD_LOGGING = os.getenv("FORCE_CLOUD_LOGGING", "False") == "True"
        self.IS_LAMBDA = "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Environment variable {key} is not set or empty")
        return value


settings = Config()
