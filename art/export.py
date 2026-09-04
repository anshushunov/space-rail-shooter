"""Переэкспорт всех art/blender/*.blend в game/assets/models/*.glb после ручных правок."""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART_BLENDER = os.path.join(HERE, "blender")
REPO = os.path.abspath(os.path.join(HERE, ".."))
MODELS = os.path.join(REPO, "game", "assets", "models")
sys.path.insert(0, ART_BLENDER)

import bpy  # noqa: E402

from lib import export  # noqa: E402

blends = sorted(glob.glob(os.path.join(ART_BLENDER, "*.blend")))
if not blends:
    raise SystemExit("EXPORT_NOTHING: нет .blend в art/blender")

for blend in blends:
    name = os.path.splitext(os.path.basename(blend))[0]
    bpy.ops.wm.open_mainfile(filepath=blend)
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        raise SystemExit(f"EXPORT_MISSING_OBJECT: в {blend} нет меш-объекта {name}")
    out = os.path.join(MODELS, f"{name}.glb")
    export.export_glb(obj, out)
    print("EXPORTED", name, out, os.path.getsize(out))
