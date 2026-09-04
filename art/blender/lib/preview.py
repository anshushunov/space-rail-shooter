"""Рендер трёх ракурсов в PNG. Не обязателен: если EEVEE не поднимается headless, возвращает []."""
import math

import bpy
from mathutils import Vector


def render_views(obj, out_prefix: str, size=(640, 480)) -> list[str]:
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        print("PREVIEW_SKIPPED engine")
        return []
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
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

    views = {"rear": (0.0, -7.0, 3.5), "side": (8.0, 0.0, 1.5), "top": (0.0, 0.0, 9.0)}
    written: list[str] = []
    try:
        for name, loc in views.items():
            cam.location = Vector(loc)
            scene.render.filepath = f"{out_prefix}-{name}.png"
            bpy.ops.render.render(write_still=True)
            written.append(scene.render.filepath)
            print("PREVIEW_WRITTEN", scene.render.filepath)
    except Exception as exc:  # noqa: BLE001
        print("PREVIEW_SKIPPED", repr(exc))
    finally:
        for o in (cam, sun):
            bpy.data.objects.remove(o, do_unlink=True)
    return written
