import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.S3_BUCKET: str = os.getenv("S3_BUCKET_NAME")
        self.MANIFEST_PATH: str = os.getenv("MANIFEST_PATH", "manifest.json")
        self.TMP_DIR: str = os.getenv("TMP_DIR", "tmp")

        self.RESOURCES: dict[str, str] = {
        "parts": os.getenv("REBRICKABLE_PARTS_CSV_URL"),
        "categories": os.getenv("REBRICKABLE_CATEGORIES_CSV_URL"),
    }

settings = Config()