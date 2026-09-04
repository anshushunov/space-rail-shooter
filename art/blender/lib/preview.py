"""Рендер трёх ракурсов в PNG. Не обязателен: если EEVEE не поднимается headless, возвращает []."""
import math

import bpy
from mathutils import Vector

# Имя движка менялось между версиями Blender: 4.2 — BLENDER_EEVEE_NEXT, 4.5+ — снова BLENDER_EEVEE.
ENGINES = ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT")
VIEWS = {"rear": (0.0, -7.0, 3.5), "side": (8.0, 0.0, 1.5), "top": (0.0, 0.0, 9.0)}


def _set_engine(scene) -> bool:
    """Ставит первый принятый движок из ENGINES. False, если ни один не подошёл."""
    for engine in ENGINES:
        try:
            scene.render.engine = engine
        except TypeError:
            continue
        return True
    return False


def render_views(obj, out_prefix: str, size=(640, 480)) -> list[str]:
    scene = bpy.context.scene
    if not _set_engine(scene):
        print("PREVIEW_SKIPPED engine")
        return []

    # Превью — вспомогательный артефакт: любая ошибка настройки сцены или рендера
    # не должна ронять сборку, поэтому весь дальнейший код внутри try/finally.
    cam = sun = None
    written: list[str] = []
    try:
        scene.render.resolution_x, scene.render.resolution_y = size
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGB"
        scene.render.image_settings.compression = 100
        world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
        scene.world = world
        world.use_nodes = True
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.02, 0.02, 0.05, 1.0)

        sun_data = bpy.data.lights.new("preview_sun", "SUN")
        sun_data.energy = 3.0
        sun = bpy.data.objects.new("preview_sun", sun_data)
        scene.collection.objects.link(sun)
        sun.rotation_euler = (math.radians(50), 0.0, math.radians(30))

        cam_data = bpy.data.cameras.new("preview_cam")
        cam = bpy.data.objects.new("preview_cam", cam_data)
        scene.collection.objects.link(cam)
        scene.camera = cam
        track = cam.constraints.new("TRACK_TO")
        track.target = obj
        track.track_axis = "TRACK_NEGATIVE_Z"
        track.up_axis = "UP_Y"

        for name, loc in VIEWS.items():
            cam.location = Vector(loc)
            scene.render.filepath = f"{out_prefix}-{name}.png"
            bpy.ops.render.render(write_still=True)
            written.append(scene.render.filepath)
            print("PREVIEW_WRITTEN", scene.render.filepath)
    except Exception as exc:  # noqa: BLE001
        print("PREVIEW_SKIPPED", repr(exc))
    finally:
        for o in (cam, sun):
            if o is not None:
                bpy.data.objects.remove(o, do_unlink=True)
    return written
