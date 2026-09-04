"""Сохранение .blend и экспорт .glb для Godot."""
import os

import bpy


def save_blend(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for img in bpy.data.images:
        if img.name == "palette" and not img.packed_file:
            img.pack()
    bpy.ops.wm.save_as_mainfile(filepath=path)


def export_glb(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
    )
