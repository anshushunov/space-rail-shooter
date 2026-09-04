"""Проверка .glb по style-guide обратным импортом в Blender. Код возврата 1 при нарушении."""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
MODELS = os.path.join(REPO, "game", "assets", "models")

# Оси Blender после импорта: X ширина, Y длина, Z высота.
LIMITS = {
    "ship": {"tris": (450, 800), "x": (3.0, 3.8), "y": (4.0, 4.6), "z": (1.6, 2.2)},
}


def check(name: str, lim: dict) -> list[str]:
    path = os.path.join(MODELS, f"{name}.glb")
    if not os.path.exists(path):
        return [f"{name}: файл не найден {path}"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    problems: list[str] = []
    if len(meshes) != 1:
        problems.append(f"{name}: мешей {len(meshes)}, ожидался 1")
        return problems
    obj = meshes[0]
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    dims = obj.dimensions
    print(f"CHECK {name}: tris={tris} dims=({dims.x:.2f}, {dims.y:.2f}, {dims.z:.2f})")
    lo, hi = lim["tris"]
    if not lo <= tris <= hi:
        problems.append(f"{name}: треугольников {tris}, допустимо {lo}–{hi}")
    for axis in "xyz":
        lo, hi = lim[axis]
        v = getattr(dims, axis)
        if not lo <= v <= hi:
            problems.append(f"{name}: размер {axis}={v:.2f}, допустимо {lo}–{hi}")
    return problems


def main() -> int:
    all_problems: list[str] = []
    for name, lim in LIMITS.items():
        all_problems.extend(check(name, lim))
    for p in all_problems:
        print("FAIL", p)
    print("CHECK_RESULT", "FAIL" if all_problems else "OK")
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
