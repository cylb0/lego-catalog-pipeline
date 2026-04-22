import sys
import logging
import os
import bpy
import addon_utils

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


def setup_argv():
    argv = sys.argv
    part_id, ldraw_dir, output_path = argv[argv.index("--") + 1 :]
    return part_id, ldraw_dir, output_path


def setup_files(part_id, output_path):
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{part_id}.glb")
    return output_file


def setup_blender(ldraw_dir):
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if bpy.context.scene.world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    bpy.context.scene.world.use_nodes = True

    addon_utils.enable("io_scene_importldraw", default_set=True)
    logger.info("ImportLDraw addon enabled")


def import_ldraw_model(part_id, ldraw_dir):
    input_file = os.path.join(ldraw_dir, "parts", f"{part_id}.dat")

    if not os.path.exists(input_file):
        logger.error(f"missing file {input_file}")
        sys.exit(1)

    try:
        bpy.ops.import_scene.importldraw(
            filepath=input_file, ldrawPath=ldraw_dir, addEnvironment=False
        )
        logger.info("Import successful")
    except Exception as e:
        logger.error(f"Import failed: {e}")
        sys.exit(1)


def export_glb(output_file):
    try:
        bpy.ops.export_scene.gltf(filepath=output_file, export_format="GLB")
        logger.info(f"Export successful to {output_file}")
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


setup_logging()
part_id, ldraw_dir, output_path = setup_argv()
output_file = setup_files(part_id, output_path)
setup_blender(ldraw_dir)
import_ldraw_model(part_id, ldraw_dir)
export_glb(output_file)
