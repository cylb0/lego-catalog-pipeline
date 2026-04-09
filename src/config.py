import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    S3_BUCKET: str = os.getenv("S3_BUCKET_NAME")
    MANIFEST_PATH: str = os.getenv("MANIFEST_PATH", "manifest.json")
    TMP_DIR: str = os.getenv("TMP_DIR", "tmp")

    RESOURCES: dict[str, str] = {
        "parts": os.getenv("REBRICKABLE_PARTS_CSV_URL"),
        "categories": os.getenv("REBRICKABLE_CATEGORIES_CSV_URL"),
    }