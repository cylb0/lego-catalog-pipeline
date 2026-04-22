import subprocess
import logging
import os

logger = logging.getLogger(__name__)


def convert_part(part_id: str, ldraw_dir: str, output_path: str):
    logger.info(f"Converting part {part_id}")
    result = subprocess.run(
        [
            "blender",
            "--background",
            "--python",
            "/app/src/conversion/blender_script.py",
            "--",
            part_id,
            ldraw_dir,
            output_path,
        ],
        capture_output=True,
        text=True,
    )
    logger.info(f"Blender output: {result.stdout}")
    logger.info(f"Blender error: {result.stderr}")
    if result.returncode != 0:
        logger.error(f"Blender failed for {part_id}: {result.stderr}")
        return False

    output_file = f"{output_path}/{part_id}.glb"

    if not os.path.exists(output_file):
        logger.error(f"Missing output file: {output_file}")
        return False

    logger.info(f"Conversion successful for part {part_id}")
    return True
