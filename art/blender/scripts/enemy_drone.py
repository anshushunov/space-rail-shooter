"""Враг-дрон: плоский клин с красным глазом. Нос по +Y. Запуск: scripts/art.sh drone."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mathutils import Vector  # noqa: E402

from lib import pipeline  # noqa: E402

NOSE_Y, TAIL_Y = 0.78, -0.72


def _t(y):
    """0 у кормы, 1 у носа — общая координата для всех сужений."""
    return min(max((y - TAIL_Y) / (NOSE_Y - TAIL_Y), 0.0), 1.0)


def taper(v):
    """К носу клин сужается по X почти в точку и слегка сплющивается по Z."""
    t = _t(v.y)
    return Vector((v.x * (1.0 - 0.88 * t), v.y, v.z * (1.0 - 0.35 * t)))


def spine_taper(v):
    """Гребень сужается мягче корпуса: на концепте это широкий капот, а не игла."""
    t = _t(v.y)
    return Vector((v.x * (1.0 - 0.55 * t), v.y, v.z * (1.0 - 0.20 * t)))


FIN_BASE_Z = 0.03


def fin_lean(v):
    """Плавник расходится наружу кверху и приподнимается к задней кромке.

    Развал по высоте (а не только по Y) — то, из-за чего пара плавников читается
    как «рога» с любого ракурса: спереди и сзади они складываются в букву V.
    """
    t = min(max((TAIL_Y - v.y) / 0.5 + 0.5, 0.0), 1.0)
    side = 1.0 if v.x > 0 else -1.0
    splay = 0.40 * max(v.z - FIN_BASE_Z, 0.0)
    return Vector((v.x + side * (0.09 * t + splay), v.y, v.z + 0.13 * t))


def build(b):
    body = b.box((1.50, NOSE_Y - TAIL_Y, 0.34), (0.0, (NOSE_Y + TAIL_Y) / 2, 0.0), "gray")
    b.deform(body, taper)
    body = b.bevel(body, offset=0.03, segments=3, cell="gray")
    # Брюхо и задняя кромка тёмные: на концепте низ клина уходит в тень.
    b.paint([f for f in body if f.normal.z < -0.5 or f.normal.y < -0.5], "gray_dark")

    spine = b.box((0.42, 1.30, 0.16), (0.0, 0.05, 0.20), "navy")
    b.deform(spine, spine_taper)
    b.bevel(spine, offset=0.02, segments=2, cell="navy")

    # Глаз: серое кольцо и красное эмиссивное ядро на самом носу.
    ring = b.cylinder(12, 0.17, 0.14, (0.0, NOSE_Y + 0.02, 0.0), "gray_dark", axis="Y")
    b.cylinder(12, 0.10, 0.16, (0.0, NOSE_Y + 0.03, 0.0), "emit_red", axis="Y")
    b.paint([f for f in ring if f.normal.y > 0.9], "navy")

    # Плавники стоят снаружи кромки клина: в виде сверху они выходят за силуэт.
    for sx in (-1.0, 1.0):
        fin = b.box((0.08, 0.54, 0.34), (sx * 0.66, -0.50, 0.20), "navy")
        b.deform(fin, fin_lean)
        b.bevel(fin, offset=0.015, segments=2, cell="navy")

    # Двигатель сидит на конце гребня; красной светится задняя грань и её фаска,
    # поэтому свет виден и сзади, и сверху.
    engine = b.box((0.44, 0.26, 0.22), (0.0, TAIL_Y + 0.02, 0.15), "navy")
    engine = b.bevel(engine, offset=0.02, segments=1, cell="navy")
    b.paint([f for f in engine if f.normal.y < -0.5], "emit_red")


pipeline.run("enemy_drone", build)
