"""Обвязка скрипта модели: reset сцены, материалы, сборка, метрики, .blend, .glb, превью.

Скрипт модели описывает только геометрию:

    from lib import pipeline
    def build(b): ...
    pipeline.run("asteroid_a", build)
"""
import os

import bpy

from . import build, export, materials, preview

ART_BLENDER = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = os.path.abspath(os.path.join(ART_BLENDER, "..", ".."))
PALETTE = os.path.join(ART_BLENDER, "palette.png")
MODELS = os.path.join(REPO, "game", "assets", "models")
REFS = os.path.join(REPO, "art", "refs")


def run(name: str, build_fn, render_preview: bool = True):
    """Строит модель `name` функцией `build_fn(builder)` и выпускает все артефакты."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    materials.ensure_palette_materials(PALETTE)

    b = build.Builder()
    build_fn(b)
    obj = b.finish(name)

    tag = name.upper()
    print(f"{tag}_TRIS", build.tri_count(obj))
    print(f"{tag}_DIMS", tuple(round(v, 2) for v in obj.dimensions))

    export.save_blend(os.path.join(ART_BLENDER, f"{name}.blend"))
    glb = os.path.join(MODELS, f"{name}.glb")
    export.export_glb(obj, glb)
    print(f"{tag}_GLB", glb, os.path.getsize(glb))

    if render_preview:
        preview.render_views(obj, os.path.join(REFS, f"preview-{name}"))
    return obj
