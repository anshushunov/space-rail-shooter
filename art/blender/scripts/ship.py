"""Корабль игрока «Жук». Запуск: blender -b --python art/blender/scripts/ship.py --python-exit-code 1."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART_BLENDER = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ART_BLENDER)

import bpy  # noqa: E402

from lib import build, export, materials, preview  # noqa: E402
from lib.build import center  # noqa: E402

PALETTE = os.path.join(ART_BLENDER, "palette.png")
BLEND = os.path.join(ART_BLENDER, "ship.blend")
GLB = os.path.join(REPO, "game", "assets", "models", "ship.glb")
PREVIEW = os.path.join(REPO, "art", "refs", "preview-ship")

bpy.ops.wm.read_factory_settings(use_empty=True)
base, emit = materials.ensure_palette_materials(PALETTE)

b = build.Builder()

# Корпус: эллипсоид, нос по +Y.
hull = b.sphere(12, 8, (1.1, 1.7, 0.8), (0.0, 0.0, 0.0), "cream")
b.paint([f for f in hull if 0.1 < center(f).y < 0.6], "orange")
b.paint([f for f in hull if center(f).z < -0.35], "navy")

# Сопло сзади (-Y) с эмиссивной задней крышкой и тёмным ядром.
nozzle = b.cylinder(12, 0.75, 0.5, (0.0, -1.65, 0.0), "navy", axis="Y")
b.paint([f for f in nozzle if f.normal.y < -0.9], "emit_cyan")
b.cylinder(12, 0.35, 0.2, (0.0, -1.95, 0.0), "black", axis="Y")

# Кокпит с одним белым бликом на верхней передней грани.
cockpit = b.sphere(8, 6, (0.45, 0.5, 0.35), (0.0, 0.5, 0.75), "navy")
highlight = max(cockpit, key=lambda f: center(f).y + center(f).z)
b.paint([highlight], "white")

# Крылышки и бластеры симметрично.
for sx in (-1.0, 1.0):
    b.box((0.6, 0.5, 0.08), (sx * 1.1, -0.9, -0.1), "cream")
    b.box((0.3, 0.5, 0.08), (sx * 1.55, -0.9, -0.1), "orange")
    b.cylinder(8, 0.06, 0.8, (sx * 0.45, 1.85, 0.15), "yellow", axis="Y")
    b.cylinder(8, 0.12, 0.25, (sx * 0.45, 1.5, 0.15), "navy", axis="Y")

ship = b.finish("ship", [base, emit])

print("SHIP_TRIS", build.tri_count(ship))
print("SHIP_DIMS", tuple(round(v, 2) for v in ship.dimensions))

export.save_blend(BLEND)
export.export_glb(ship, GLB)
print("SHIP_GLB", GLB, os.path.getsize(GLB))
preview.render_views(ship, PREVIEW)
