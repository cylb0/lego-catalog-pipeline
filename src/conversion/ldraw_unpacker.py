import os
import zipfile
import logging

logger = logging.getLogger(__name__)


def extract_ldraw_zip(zip_path: str, extract_dir: str):
    if not os.path.exists(extract_dir):
        logger.info(f"Creating extraction dir: {extract_dir}")
        os.makedirs(extract_dir, exist_ok=True)

    logger.info(f"Extracting {zip_path} -> {extract_dir}")

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    logger.info("Extraction complete")

    ldraw_root = os.path.join(extract_dir, "complete/ldraw")

    if not os.path.exists(ldraw_root):
        raise FileNotFoundError(f"Ldraw root not found at {ldraw_root}")

    return ldraw_root
