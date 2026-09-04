"""Три варианта астероида из икосферы: детерминированный шум по вершинам. Запуск: scripts/art.sh asteroid."""
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

from lib import build, pipeline  # noqa: E402

VARIANTS = {"asteroid_a": 11, "asteroid_b": 23, "asteroid_c": 37}
SUBDIVISIONS = 3      # 320 треугольников: 2 дают всего 80 — ниже лимита проверки
RADIUS = 1.5          # под коллайдер SphereShape3D r=1.5
BUMP = 0.20           # крупные неровности
GRAIN = 0.05          # мелкая шероховатость
DARK_SHARE = 0.15     # доля тёмных пятен


def make_build(seed: int):
    def build_fn(b):
        rng = random.Random(seed)
        shell = bmesh.ops.create_icosphere(b.bm, subdivisions=SUBDIVISIONS, radius=1.0)
        verts = shell["verts"]
        # Смещение в поле шума: у каждого варианта свой кусок одного и того же
        # детерминированного поля, поэтому силуэты разные, а сборка повторяемая.
        offset = Vector(rng.uniform(-40.0, 40.0) for _ in range(3))
        for v in verts:
            big = noise.noise(v.co * 1.6 + offset)
            fine = noise.noise(v.co * 4.5 + offset * 0.5)
            v.co = v.co * (1.0 + BUMP * big + GRAIN * fine)
        axes = [1.0, 0.9, 0.8]
        rng.shuffle(axes)
        matrix = Matrix.Diagonal((axes[0] * RADIUS, axes[1] * RADIUS, axes[2] * RADIUS, 1.0))
        bmesh.ops.transform(b.bm, matrix=matrix, verts=verts)

        faces = b.adopt(verts, "rock")
        b.paint([f for f in faces if f.normal.z > 0.55], "rock_light")
        # Порядок граней от bmesh.ops зависит от адресов в памяти и меняется от
        # процесса к процессу: если раздавать rng.random() в этом порядке, тёмные
        # пятна выпадают на разные грани и байты .glb пляшут. Ключ — координаты.
        ordered = sorted(faces, key=lambda f: tuple(round(c, 5) for c in build.center(f)))
        b.paint([f for f in ordered if rng.random() < DARK_SHARE], "rock_dark")
    return build_fn


for name, seed in VARIANTS.items():
    pipeline.run(name, make_build(seed))
