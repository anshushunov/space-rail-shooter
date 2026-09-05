"""Враг-стрелок: бронированная турель с двумя излучателями. Нос по +Y. Запуск: scripts/art.sh shooter."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mathutils import Vector  # noqa: E402

from lib import pipeline  # noqa: E402

FRONT_Y, REAR_Y = 0.90, -0.90


def nose_taper(v):
    """Корпус к носу слегка сужается и снижается, как у концепта."""
    t = min(max((v.y - REAR_Y) / (FRONT_Y - REAR_Y), 0.0), 1.0)
    return Vector((v.x * (1.0 - 0.18 * t), v.y, v.z * (1.0 - 0.22 * t) - 0.04 * t))


def shoulder_sweep(v):
    """Плечевой блок уходит назад и вниз к внешнему краю — наплечник, а не полка."""
    t = min(max((abs(v.x) - 0.52) / 0.6, 0.0), 1.0)
    return Vector((v.x, v.y - 0.32 * t, v.z - 0.16 * t))


def build(b):
    hull = b.box((1.40, FRONT_Y - REAR_Y, 0.70), (0.0, 0.0, 0.0), "gray")
    b.deform(hull, nose_taper)
    hull = b.bevel(hull, offset=0.06, segments=3, cell="gray")
    b.paint([f for f in hull if f.normal.z < -0.6], "gray_dark")

    slot = b.box((0.52, 1.24, 0.18), (0.0, 0.12, 0.36), "navy")
    b.deform(slot, nose_taper)
    b.bevel(slot, offset=0.02, segments=2, cell="navy")

    for sx in (-1.0, 1.0):
        shoulder = b.box((0.58, 1.00, 0.52), (sx * 0.84, 0.10, 0.16), "gray")
        b.deform(shoulder, shoulder_sweep)
        shoulder = b.bevel(shoulder, offset=0.04, segments=2, cell="gray")
        b.paint([f for f in shoulder if f.normal.z < -0.5], "gray_dark")

        pod = b.cylinder(12, 0.21, 0.90, (sx * 0.95, 0.50, -0.14), "gray_dark", axis="Y")
        b.paint([f for f in pod if f.normal.y > 0.9], "navy")
        # Бронированный хомут на стволе: на концепте ствол не голая труба.
        collar = b.box((0.34, 0.34, 0.34), (sx * 0.95, 0.30, -0.14), "gray")
        b.bevel(collar, offset=0.04, segments=1, cell="gray")
        b.cylinder(12, 0.12, 0.16, (sx * 0.95, 0.98, -0.14), "emit_magenta", axis="Y")

        # Двигатель светится и назад, и вверх: на концепте красные колпаки видно
        # с любого ракурса, включая фронтальный.
        engine = b.cylinder(12, 0.16, 0.36, (sx * 0.45, REAR_Y - 0.05, 0.34), "navy", axis="Y")
        b.paint([f for f in engine if f.normal.y < -0.9 or f.normal.z > 0.5], "emit_red")

    for gx in (-0.42, -0.14, 0.14, 0.42):
        b.box((0.18, 0.06, 0.08), (gx, FRONT_Y, -0.16), "emit_red")


pipeline.run("enemy_shooter", build)
