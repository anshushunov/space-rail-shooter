"""Корабль игрока «Жук». Запуск: blender -b --python-exit-code 1 --python art/blender/scripts/ship.py."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART_BLENDER = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ART_BLENDER)

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from lib import build, export, materials, preview  # noqa: E402
from lib.build import center  # noqa: E402

PALETTE = os.path.join(ART_BLENDER, "palette.png")
BLEND = os.path.join(ART_BLENDER, "ship.blend")
GLB = os.path.join(REPO, "game", "assets", "models", "ship.glb")
PREVIEW = os.path.join(REPO, "art", "refs", "preview-ship")

bpy.ops.wm.read_factory_settings(use_empty=True)
materials.ensure_palette_materials(PALETTE)

b = build.Builder()

# --- корпус ------------------------------------------------------------------
# Тело вращения вокруг Y, нос по +Y. Сечение эллиптическое: шире, чем выше.
# Узкие пояса профиля нужны, чтобы попасть в них оранжевыми полосами концепта.
HULL = [
    (0.00, 1.75),
    (0.38, 1.58),
    (0.72, 1.18),
    (0.93, 0.70),
    (0.98, 0.46),
    (1.00, 0.22),   # пояс 0.22…0.46 — передняя оранжевая полоса
    (0.99, -0.30),
    (0.92, -0.72),
    (0.88, -0.92),
    (0.82, -1.10),  # пояс -1.10…-0.92 — задняя оранжевая полоса, видна сзади
    (0.68, -1.32),
    (0.56, -1.48),
    (0.45, -1.60),  # пояс -1.60…-1.48 — светлый ободок у кормы
]
hull = b.lathe(HULL, 32, (0.0, 0.0, 0.0), "cream", scale=(1.1, 0.8))
b.paint([f for f in hull if 0.25 < center(f).y < 0.45], "orange")
b.paint([f for f in hull if -1.09 < center(f).y < -0.93], "orange")
b.paint([f for f in hull if center(f).z < -0.30], "navy")
b.paint([f for f in hull if center(f).y < -1.50], "navy_light")

# --- двигатель ---------------------------------------------------------------
# Барабан начинается внутри корпуса и выходит наружу уступом; задняя кромка
# скошена, дальше плоское кольцо, которое красится в эмиссию.
DRUM = [
    (0.42, -1.45),
    (0.52, -1.60),
    (0.55, -1.86),
    (0.52, -1.94),
    (0.44, -1.95),
    (0.33, -1.95),  # плоское кольцо 0.33…0.44 — свечение
]
# Сечение приплюснуто сильнее корпуса: так узел двигателя занимает меньше
# высоты силуэта и не спорит с корпусом.
DRUM_SCALE = (1.15, 0.72)
drum = b.lathe(DRUM, 24, (0.0, 0.0, 0.0), "navy", scale=DRUM_SCALE, cap=False)
b.paint([f for f in drum if center(f).y < -1.949], "emit_cyan")

# Жерло: воронка внутрь корпуса. Нормали развёрнуты, иначе односторонний
# материал покажет дыру насквозь.
b.lathe([(0.00, -1.66), (0.22, -1.80), (0.33, -1.95)], 24, (0.0, 0.0, 0.0), "black",
        scale=DRUM_SCALE, cap=False, flip=True)

# Блок вентиляции сверху кормы с решёткой из трёх тёмных пластин.
vent = b.box((0.55, 0.45, 0.34), (0.0, -1.30, 0.50), "navy")
b.bevel(vent, offset=0.03, segments=2, cell="navy")
for gx in (-0.16, 0.0, 0.16):
    b.box((0.07, 0.10, 0.22), (gx, -1.50, 0.50), "black")

# --- кокпит ------------------------------------------------------------------
b.cylinder(16, 0.55, 0.30, (0.0, 0.55, 0.65), "navy_light", axis="Z")
cockpit = b.sphere(16, 8, (0.42, 0.55, 0.34), (0.0, 0.55, 0.74), "navy")


# Блик — не веер у полюса, а пара граней пояса ниже макушки: так он читается
# прямоугольным пятном, как на концепте.
b.paint([f for f in cockpit if 0.94 < center(f).z < 1.05 and center(f).y > 0.78], "white")

# --- крылья, бластеры, воздухозаборники --------------------------------------
WING_ROOT_X, WING_TIP_X, WING_Y = 0.70, 1.75, -0.80


def sweep(v):
    """Стреловидность: к концу крыло уходит назад, сужается и слегка опускается."""
    t = min(max((abs(v.x) - WING_ROOT_X) / (WING_TIP_X - WING_ROOT_X), 0.0), 1.0)
    return Vector((v.x,
                   WING_Y + (v.y - WING_Y) * (1.0 - 0.47 * t) - 0.40 * t,
                   v.z - 0.05 * t))


def tilt(v):
    """Усики бластеров отклоняются вверх, как на концепте."""
    return Vector((v.x, v.y, v.z + 0.22 * max(v.y - 1.35, 0.0)))


for sx in (-1.0, 1.0):
    # Две коробки встык: после фаски шов читается как расшивка, а не как щель.
    wing = b.box((0.76, 0.85, 0.12), (sx * 1.08, WING_Y, -0.05), "cream")
    wing_tip = b.box((0.33, 0.85, 0.12), (sx * 1.585, WING_Y, -0.05), "orange")
    b.deform(wing + wing_tip, sweep)
    b.bevel(wing, offset=0.02, segments=2, cell="cream")
    b.bevel(wing_tip, offset=0.02, segments=2, cell="orange")
    fin = b.box((0.06, 0.30, 0.30), (sx * 1.68, -1.24, 0.02), "orange")
    b.bevel(fin, offset=0.02, segments=1, cell="orange")

    barrel = b.cylinder(12, 0.13, 0.30, (sx * 0.50, 1.45, 0.12), "navy", axis="Y")
    rod = b.cylinder(12, 0.055, 0.85, (sx * 0.50, 1.90, 0.12), "yellow", axis="Y")
    bead = b.sphere(8, 6, (0.09, 0.09, 0.09), (sx * 0.50, 2.33, 0.12), "emit_yellow")
    b.deform(barrel + rod + bead, tilt)

    intake = b.cylinder(12, 0.16, 0.50, (sx * 1.05, 0.10, 0.05), "navy", axis="Y")
    b.paint([f for f in intake if f.normal.y < -0.9], "black")

# --- брюшная плита -----------------------------------------------------------
belly = b.box((0.90, 1.40, 0.28), (0.0, -0.10, -0.74), "navy_light")
b.bevel(belly, offset=0.03, segments=2, cell="navy_light")

ship = b.finish("ship")

print("SHIP_TRIS", build.tri_count(ship))
print("SHIP_DIMS", tuple(round(v, 2) for v in ship.dimensions))

export.save_blend(BLEND)
export.export_glb(ship, GLB)
print("SHIP_GLB", GLB, os.path.getsize(GLB))
preview.render_views(ship, PREVIEW)
