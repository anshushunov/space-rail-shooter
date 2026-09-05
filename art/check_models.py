"""Проверка .glb по style-guide обратным импортом в Blender. Код возврата 1 при нарушении."""
import glob
import os
import sys

try:  # модуль импортируется юнит-тестами вне Blender
    import bpy
except ImportError:  # pragma: no cover - вне Blender
    bpy = None

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
MODELS = os.path.join(REPO, "game", "assets", "models")

# Оси Blender после импорта: X ширина, Y длина, Z высота.
ASTEROID = {"tris": (250, 600), "x": (2.0, 3.8), "y": (2.0, 3.8), "z": (2.0, 3.8)}
LIMITS = {
    "ship": {"tris": (1500, 3000), "x": (3.0, 3.8), "y": (4.0, 4.6), "z": (1.6, 2.2)},
    "asteroid_a": ASTEROID,
    "asteroid_b": ASTEROID,
    "asteroid_c": ASTEROID,
    "enemy_drone": {"tris": (500, 800), "x": (1.3, 1.9), "y": (1.2, 1.8), "z": (0.35, 0.7)},
}


def evaluate(name: str, tris: int, dims: tuple[float, float, float], lim: dict) -> list[str]:
    """Сверяет уже измеренные метрики с лимитами. Без bpy — тестируется обычным Python."""
    problems: list[str] = []
    lo, hi = lim["tris"]
    if not lo <= tris <= hi:
        problems.append(f"{name}: треугольников {tris}, допустимо {lo}–{hi}")
    for axis, v in zip("xyz", dims):
        lo, hi = lim[axis]
        if not lo <= v <= hi:
            problems.append(f"{name}: размер {axis}={v:.2f}, допустимо {lo}–{hi}")
    return problems


def check(name: str, lim: dict) -> list[str]:
    path = os.path.join(MODELS, f"{name}.glb")
    if not os.path.exists(path):
        return [f"{name}: файл не найден {path}"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(meshes) != 1:
        return [f"{name}: мешей {len(meshes)}, ожидался 1"]
    obj = meshes[0]
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    dims = (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)
    print(f"CHECK {name}: tris={tris} dims=({dims[0]:.2f}, {dims[1]:.2f}, {dims[2]:.2f})")
    return evaluate(name, tris, dims, lim)


def unknown_models() -> list[str]:
    """Модель без записи в LIMITS не проверена ничем — это тоже нарушение."""
    known = set(LIMITS)
    present = {os.path.splitext(os.path.basename(p))[0]
               for p in glob.glob(os.path.join(MODELS, "*.glb"))}
    return [f"{name}: нет записи в LIMITS" for name in sorted(present - known)]


def main() -> int:
    all_problems: list[str] = []
    for name, lim in LIMITS.items():
        all_problems.extend(check(name, lim))
    all_problems.extend(unknown_models())
    for p in all_problems:
        print("FAIL", p)
    print("CHECK_RESULT", "FAIL" if all_problems else "OK")
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
