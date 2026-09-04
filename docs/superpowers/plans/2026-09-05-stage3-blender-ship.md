# Этап 3: пайплайн Blender и корабль игрока — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Модель корабля «Жук», построенная Python-скриптом в Blender 5.2, экспортируется в `.glb` и заменяет капсулу в игре; пайплайн задокументирован командами.

**Architecture:** Библиотека `art/blender/lib/` (палитра, материалы, bmesh-сборка, экспорт, превью) и скрипты `art/blender/scripts/*.py`, запускаемые `blender -b --python`. Раскраска через UV в центры ячеек палитры 8×8, два материала (`palette`, `palette_emit`). Проверка `.glb` обратным импортом в Blender. Godot ничего нового не требует: `ModelSlot` подхватывает `res://assets/models/ship.glb`.

**Tech Stack:** Blender 5.2.1 LTS (`bpy`, `bmesh`), Python 3.12 для unittest, Godot 4.7.1 mono, Git Bash.

**Спека:** `docs/superpowers/specs/2026-09-05-stage3-blender-ship-design.md`.

## Global Constraints

- Blender: `BLENDER="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"`. Все запуски headless: `"$BLENDER" -b --python-exit-code 1 --python <script>` (флаг строго **до** `--python`: Blender обрабатывает аргументы по порядку, иначе исключения дают exit 0; найдено финальным ревью 2026-09-05).
- Godot: `GODOT="/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe"`. Импорт: `"$GODOT" --headless --path game --import`. Smoke: `"$GODOT" --headless --path game --quit-after 300` без `ERROR`/`SCRIPT ERROR`/`Unhandled exception`. Скриншот: `"$GODOT" --path game -s res://tools/screenshot.gd -- <сек> <res://путь.png>` (открывает окно на несколько секунд).
- Ось носа: Blender **+Y** → Godot −Z. 1 единица = 1 м.
- Палитра 8×8, текстура 256×256, ячейка 32 px, ячейка = `(col, row)`, `row 0` внизу изображения (порядок пикселей bpy). UV грани = центр ячейки `((col+0.5)/8, (row+0.5)/8)`. Строки 6 и 7 эмиссивные.
- Материалы: `palette` (Base Color ← текстура) и `palette_emit` (Base Color и Emission Color ← текстура, Emission Strength 3.0). Индекс материала грани: 1 для эмиссивных ячеек, иначе 0.
- Объект и меш корабля называются `ship`. Один объект, один меш. Shade smooth by angle 30°.
- Лимиты `ship.glb` (оси Blender после обратного импорта): треугольники 450–800, X 3.0–3.8, Y 4.0–4.6, Z 1.6–2.2.
- `lib/__init__.py` и `lib/palette.py` не импортируют `bpy` на уровне модуля (тесты идут в обычном Python 3.12).
- Файлы UTF-8 без BOM. Коммиты Conventional Commits на русском, без упоминания LLM. `.uid` и `.import` коммитятся.
- Пути в скриптах абсолютные, вычисляются от `__file__`. Репозиторий `C:\gamedev\prototype-blender`.

---

## Карта файлов

| Файл | Ответственность |
|---|---|
| `art/blender/lib/__init__.py` | пустой, пакет |
| `art/blender/lib/palette.py` | цвета, имена ячеек, `cell_uv`, `is_emissive`, `pixels_rgba`, `write_png` |
| `art/blender/lib/materials.py` | `ensure_palette_materials(path)` |
| `art/blender/lib/build.py` | `Builder`: `sphere`, `cylinder`, `box`, `paint`, `finish`, `center`, `tri_count` |
| `art/blender/lib/export.py` | `save_blend`, `export_glb` |
| `art/blender/lib/preview.py` | `render_views` (опционально, EEVEE) |
| `art/blender/scripts/make_palette.py` | генерирует `art/blender/palette.png` и копию в `game/assets/textures/` |
| `art/blender/scripts/ship.py` | строит корабль, сохраняет `.blend`, экспортирует `.glb`, рендерит превью |
| `art/export.py` | переэкспорт всех `.blend` → `.glb` |
| `art/check_models.py` | проверка `.glb` по лимитам, код возврата |
| `art/tests/test_palette.py` | unittest палитры |
| `scripts/art.sh` | единая точка входа для команд |
| `CLAUDE.md`, `README.md`, `docs/style-guide.md` | документация команд и решений |

---

### Task 1: Палитра, тесты и точка входа `scripts/art.sh`

**Files:**
- Create: `art/blender/lib/__init__.py`, `art/blender/lib/palette.py`, `art/tests/test_palette.py`, `art/blender/scripts/make_palette.py`, `scripts/art.sh`
- Create (generated): `art/blender/palette.png`, `game/assets/textures/palette.png`, `game/assets/textures/palette.png.import`

**Interfaces:**
- Produces:
  ```python
  # art/blender/lib/palette.py
  SIZE = 8; CELL_PX = 32; TEXTURE_PX = 256
  COLORS: dict[tuple[int, int], str]      # (col, row) -> "#RRGGBB"
  NAMES: dict[str, tuple[int, int]]       # "cream" -> (0, 0) ...
  EMISSIVE_ROWS = {6, 7}
  def resolve(cell: str | tuple[int, int]) -> tuple[int, int]
  def hex_to_rgb(hex_color: str) -> tuple[float, float, float]
  def cell_uv(cell) -> tuple[float, float]
  def is_emissive(cell) -> bool
  def pixels_rgba() -> list[float]         # 256*256*4, порядок bpy (снизу вверх)
  def write_png(path: str) -> None         # импортирует bpy внутри
  ```
  `scripts/art.sh` с командами `test | make-palette | ship | export | check | import | shot [sec] [out]`.

- [ ] **Step 1: Написать падающий тест `art/tests/test_palette.py`**

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "blender"))

from lib import palette  # noqa: E402


class PaletteTests(unittest.TestCase):
    def test_cell_uv_is_cell_center(self):
        self.assertEqual(palette.cell_uv((0, 0)), (0.0625, 0.0625))
        self.assertEqual(palette.cell_uv((7, 7)), (0.9375, 0.9375))
        self.assertEqual(palette.cell_uv("cream"), palette.cell_uv((0, 0)))

    def test_every_name_points_to_defined_color(self):
        for name, cell in palette.NAMES.items():
            self.assertIn(cell, palette.COLORS, name)

    def test_colors_are_valid_unique_hex(self):
        seen = set()
        for cell, color in palette.COLORS.items():
            self.assertRegex(color, r"^#[0-9A-F]{6}$", str(cell))
            self.assertNotIn(color, seen, f"дубликат {color}")
            seen.add(color)
            self.assertTrue(0 <= cell[0] < palette.SIZE and 0 <= cell[1] < palette.SIZE)

    def test_emissive_rows(self):
        self.assertTrue(palette.is_emissive("emit_cyan"))
        self.assertTrue(palette.is_emissive("emit_red"))
        self.assertFalse(palette.is_emissive("cream"))
        self.assertFalse(palette.is_emissive("yellow"))

    def test_hex_to_rgb(self):
        self.assertEqual(palette.hex_to_rgb("#FFFFFF"), (1.0, 1.0, 1.0))
        r, g, b = palette.hex_to_rgb("#F08A3C")
        self.assertAlmostEqual(r, 0xF0 / 255)
        self.assertAlmostEqual(g, 0x8A / 255)
        self.assertAlmostEqual(b, 0x3C / 255)

    def test_pixels_have_cell_colors_at_cell_centers(self):
        px = palette.pixels_rgba()
        self.assertEqual(len(px), palette.TEXTURE_PX * palette.TEXTURE_PX * 4)

        def at(col, row):
            x = col * palette.CELL_PX + palette.CELL_PX // 2
            y = row * palette.CELL_PX + palette.CELL_PX // 2
            i = (y * palette.TEXTURE_PX + x) * 4
            return tuple(px[i:i + 3]), px[i + 3]

        rgb, a = at(0, 0)
        self.assertEqual(a, 1.0)
        for got, want in zip(rgb, palette.hex_to_rgb(palette.COLORS[(0, 0)])):
            self.assertAlmostEqual(got, want)
        rgb, _ = at(7, 7)  # незанятая ячейка чёрная
        self.assertEqual(rgb, (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Запустить и убедиться, что падает**

Run: `python -m unittest discover -s art/tests -v 2>&1 | tail -5`
Expected: `ModuleNotFoundError: No module named 'lib'`.

- [ ] **Step 3: Создать `art/blender/lib/__init__.py`** (пустой файл) **и `art/blender/lib/palette.py`**

```python
"""Палитра 8×8 для всех моделей игры. Без импорта bpy на уровне модуля."""

SIZE = 8
CELL_PX = 32
TEXTURE_PX = SIZE * CELL_PX

# (col, row) -> цвет. row 0 — нижний ряд изображения (порядок пикселей bpy).
COLORS: dict[tuple[int, int], str] = {
    (0, 0): "#F2E9D8", (1, 0): "#D9CDB8", (2, 0): "#FFFFFF",
    (0, 1): "#F08A3C", (1, 1): "#C96A22",
    (0, 2): "#1E2A4A", (1, 2): "#2F3F6B", (2, 2): "#10162A",
    (0, 3): "#FFD23F",
    (0, 4): "#8A94A6", (1, 4): "#5B6478",
    (0, 5): "#6E5A4B", (1, 5): "#4E3F35", (2, 5): "#8C7561",
    (0, 6): "#40E0FF", (1, 6): "#A8F0FF",
    (0, 7): "#FFE566", (1, 7): "#FF4A3D", (2, 7): "#FF5AC8",
}

NAMES: dict[str, tuple[int, int]] = {
    "cream": (0, 0), "cream_dark": (1, 0), "white": (2, 0),
    "orange": (0, 1), "orange_dark": (1, 1),
    "navy": (0, 2), "navy_light": (1, 2), "black": (2, 2),
    "yellow": (0, 3),
    "gray": (0, 4), "gray_dark": (1, 4),
    "rock": (0, 5), "rock_dark": (1, 5), "rock_light": (2, 5),
    "emit_cyan": (0, 6), "emit_cyan_pale": (1, 6),
    "emit_yellow": (0, 7), "emit_red": (1, 7), "emit_magenta": (2, 7),
}

EMISSIVE_ROWS = {6, 7}


def resolve(cell) -> tuple[int, int]:
    """Имя ячейки или (col, row) -> (col, row)."""
    if isinstance(cell, str):
        return NAMES[cell]
    return (int(cell[0]), int(cell[1]))


def hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def cell_uv(cell) -> tuple[float, float]:
    col, row = resolve(cell)
    return ((col + 0.5) / SIZE, (row + 0.5) / SIZE)


def is_emissive(cell) -> bool:
    return resolve(cell)[1] in EMISSIVE_ROWS


def pixels_rgba() -> list[float]:
    """Плоский RGBA-буфер 256×256 в порядке bpy: строки снизу вверх."""
    px: list[float] = []
    for y in range(TEXTURE_PX):
        row = y // CELL_PX
        for x in range(TEXTURE_PX):
            col = x // CELL_PX
            r, g, b = hex_to_rgb(COLORS.get((col, row), "#000000"))
            px.extend((r, g, b, 1.0))
    return px


def write_png(path: str) -> None:
    """Сохраняет палитру через bpy без сторонних библиотек."""
    import bpy  # noqa: PLC0415

    img = bpy.data.images.get("palette_gen")
    if img is not None:
        bpy.data.images.remove(img)
    img = bpy.data.images.new("palette_gen", TEXTURE_PX, TEXTURE_PX, alpha=False)
    img.pixels = pixels_rgba()
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
```

- [ ] **Step 4: Прогнать тесты**

Run: `python -m unittest discover -s art/tests -v 2>&1 | tail -3`
Expected: `OK`, 6 тестов.

- [ ] **Step 5: Создать `art/blender/scripts/make_palette.py`**

```python
"""Генерирует palette.png для Blender и копию для Godot. Запуск: blender -b --python этот_файл."""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ART_BLENDER = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ART_BLENDER)

from lib import palette  # noqa: E402

OUT = os.path.join(ART_BLENDER, "palette.png")
GODOT_OUT = os.path.join(REPO, "game", "assets", "textures", "palette.png")

palette.write_png(OUT)
os.makedirs(os.path.dirname(GODOT_OUT), exist_ok=True)
shutil.copyfile(OUT, GODOT_OUT)

# Контроль: прочитать обратно и сверить центр ячейки (0,0).
import bpy  # noqa: E402

check = bpy.data.images.load(OUT)
w = check.size[0]
c = palette.CELL_PX // 2
i = (c * w + c) * 4
got = tuple(round(v, 3) for v in check.pixels[i:i + 3])
want = tuple(round(v, 3) for v in palette.hex_to_rgb(palette.COLORS[(0, 0)]))
print("PALETTE_WRITTEN", OUT, check.size[:], "cell00", got, "want", want)
if any(abs(a - b) > 2 / 255 for a, b in zip(got, want)):
    raise SystemExit("PALETTE_COLOR_MISMATCH")
```

- [ ] **Step 6: Создать `scripts/art.sh`**

```bash
#!/usr/bin/env bash
# Единая точка входа арт-пайплайна. Запуск из любого места: scripts/art.sh <команда>.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER="${BLENDER:-/c/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
GODOT="${GODOT:-/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe}"

blender_run() { "$BLENDER" -b --python-exit-code 1 --python "$1"; }

cmd="${1:-}"
shift || true
case "$cmd" in
  test)         (cd "$ROOT" && python -m unittest discover -s art/tests -v) ;;
  make-palette) blender_run "$ROOT/art/blender/scripts/make_palette.py" ;;
  ship)         blender_run "$ROOT/art/blender/scripts/ship.py" ;;
  export)       blender_run "$ROOT/art/export.py" ;;
  check)        blender_run "$ROOT/art/check_models.py" ;;
  import)       "$GODOT" --headless --path "$ROOT/game" --import ;;
  shot)         "$GODOT" --path "$ROOT/game" -s res://tools/screenshot.gd -- "${1:-2.5}" "${2:-res://../docs/playtests/shot.png}" ;;
  *)
    echo "usage: scripts/art.sh {test|make-palette|ship|export|check|import|shot [sec] [res://out.png]}" >&2
    exit 2 ;;
esac
```

Сделать исполняемым: `chmod +x scripts/art.sh` (в Git Bash на Windows это выставит бит в индексе через `git update-index --chmod=+x scripts/art.sh` после `git add`).

- [ ] **Step 7: Сгенерировать палитру и импортировать в Godot**

```bash
scripts/art.sh make-palette 2>&1 | rg "PALETTE_WRITTEN|MISMATCH|Error|Traceback"
scripts/art.sh import 2>&1 | rg -c "ERROR" || true
ls -la art/blender/palette.png game/assets/textures/
```
Expected: `PALETTE_WRITTEN ... [256, 256] cell00 (0.949, 0.914, 0.847) want (0.949, 0.914, 0.847)`; в `game/assets/textures/` лежат `palette.png` и `palette.png.import`; `rg -c ERROR` печатает ничего.

Открыть `art/blender/palette.png` через Read и убедиться глазами: 8×8 сетка, слева внизу кремовый, верхние два ряда циан и жёлтый/красный/маджента, остальное чёрное.

- [ ] **Step 8: Commit**

```bash
git add art/blender/lib/__init__.py art/blender/lib/palette.py art/tests/test_palette.py art/blender/scripts/make_palette.py scripts/art.sh art/blender/palette.png game/assets/textures/palette.png game/assets/textures/palette.png.import
git update-index --chmod=+x scripts/art.sh
git commit -m "feat(art): палитра 8×8, тесты и точка входа scripts/art.sh"
```

---

### Task 2: Библиотека сборки и скрипт корабля

**Files:**
- Create: `art/blender/lib/materials.py`, `art/blender/lib/build.py`, `art/blender/lib/export.py`, `art/blender/lib/preview.py`, `art/blender/scripts/ship.py`
- Create (generated): `art/blender/ship.blend`, `game/assets/models/ship.glb`, `art/refs/preview-ship-*.png` (если EEVEE отработал headless)

**Interfaces:**
- Consumes: `lib.palette` из Task 1.
- Produces:
  ```python
  # materials.py
  def ensure_palette_materials(palette_path: str) -> tuple[bpy.types.Material, bpy.types.Material]  # (palette, palette_emit)
  # build.py
  class Builder:
      def sphere(self, segments, rings, scale, location, cell) -> list[BMFace]
      def cylinder(self, segments, radius, depth, location, cell, axis="Y") -> list[BMFace]
      def box(self, scale, location, cell) -> list[BMFace]
      def paint(self, faces, cell) -> None
      def finish(self, name, materials, smooth_angle_deg=30.0) -> bpy.types.Object
  def center(face) -> Vector
  def tri_count(obj) -> int
  # export.py
  def save_blend(path: str) -> None
  def export_glb(obj, path: str) -> None
  # preview.py
  def render_views(obj, out_prefix: str, size=(640, 480)) -> list[str]  # пути PNG; [] если рендер недоступен
  ```
  Скрипт `ship.py` печатает `SHIP_TRIS <n>` и `SHIP_DIMS (x, y, z)`.

- [ ] **Step 1: Создать `art/blender/lib/materials.py`**

```python
"""Два материала на одну палитру: базовый и эмиссивный."""
import bpy


def ensure_palette_materials(palette_path: str):
    img = bpy.data.images.get("palette")
    if img is None:
        img = bpy.data.images.load(palette_path)
        img.name = "palette"
    img.colorspace_settings.name = "sRGB"
    return _make("palette", img, emissive=False), _make("palette_emit", img, emissive=True)


def _make(name: str, img, emissive: bool):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    bsdf.inputs["Roughness"].default_value = 0.6
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emissive:
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 3.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat
```

- [ ] **Step 2: Создать `art/blender/lib/build.py`**

```python
"""bmesh-сборка low-poly моделей с покраской граней в ячейки палитры."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import palette


def center(face) -> Vector:
    return face.calc_center_median()


def tri_count(obj) -> int:
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


class Builder:
    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    # --- примитивы -----------------------------------------------------
    def sphere(self, segments, rings, scale, location, cell):
        m = Matrix.Translation(Vector(location)) @ Matrix.Diagonal((*scale, 1.0))
        r = bmesh.ops.create_uvsphere(self.bm, u_segments=segments, v_segments=rings, radius=1.0, matrix=m)
        return self._finish_part(r["verts"], cell)

    def cylinder(self, segments, radius, depth, location, cell, axis="Y"):
        rot = {"Z": Matrix.Identity(4), "Y": Matrix.Rotation(math.radians(90), 4, "X"),
               "X": Matrix.Rotation(math.radians(90), 4, "Y")}[axis]
        m = Matrix.Translation(Vector(location)) @ rot
        r = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segments,
                                  radius1=radius, radius2=radius, depth=depth, matrix=m)
        return self._finish_part(r["verts"], cell)

    def box(self, scale, location, cell):
        m = Matrix.Translation(Vector(location)) @ Matrix.Diagonal((*scale, 1.0))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=m)
        return self._finish_part(r["verts"], cell)

    # --- покраска -------------------------------------------------------
    def paint(self, faces, cell):
        u, v = palette.cell_uv(cell)
        index = 1 if palette.is_emissive(cell) else 0
        for f in faces:
            f.material_index = index
            for loop in f.loops:
                loop[self.uv].uv = (u, v)

    # --- завершение -------------------------------------------------------
    def finish(self, name, materials, smooth_angle_deg=30.0):
        mesh = bpy.data.meshes.new(name)
        self.bm.to_mesh(mesh)
        self.bm.free()
        for mat in materials:
            mesh.materials.append(mat)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(smooth_angle_deg), keep_sharp_edges=False)
        return obj

    def _finish_part(self, verts, cell):
        vs = set(verts)
        faces = [f for f in self.bm.faces if all(v in vs for v in f.verts)]
        self.bm.normal_update()
        self.paint(faces, cell)
        return faces
```

- [ ] **Step 3: Создать `art/blender/lib/export.py`**

```python
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
```

- [ ] **Step 4: Создать `art/blender/lib/preview.py`**

```python
"""Рендер трёх ракурсов в PNG. Не обязателен: если EEVEE не поднимается headless, возвращает []."""
import math

import bpy
from mathutils import Vector


def render_views(obj, out_prefix: str, size=(640, 480)) -> list[str]:
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except TypeError:
        print("PREVIEW_SKIPPED engine")
        return []
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.02, 0.05, 1.0)

    sun_data = bpy.data.lights.new("preview_sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("preview_sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0.0, math.radians(30))

    cam_data = bpy.data.cameras.new("preview_cam")
    cam = bpy.data.objects.new("preview_cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    track = cam.constraints.new("TRACK_TO")
    track.target = obj
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    views = {"rear": (0.0, -7.0, 3.5), "side": (8.0, 0.0, 1.5), "top": (0.0, 0.0, 9.0)}
    written: list[str] = []
    try:
        for name, loc in views.items():
            cam.location = Vector(loc)
            scene.render.filepath = f"{out_prefix}-{name}.png"
            bpy.ops.render.render(write_still=True)
            written.append(scene.render.filepath)
            print("PREVIEW_WRITTEN", scene.render.filepath)
    except Exception as exc:  # noqa: BLE001
        print("PREVIEW_SKIPPED", repr(exc))
    finally:
        for o in (cam, sun):
            bpy.data.objects.remove(o, do_unlink=True)
    return written
```

- [ ] **Step 5: Создать `art/blender/scripts/ship.py`**

```python
"""Корабль игрока «Жук». Запуск: blender -b --python-exit-code 1 --python art/blender/scripts/ship.py."""
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
```

- [ ] **Step 6: Запустить и проверить числа**

```bash
scripts/art.sh ship 2>&1 | rg "SHIP_|PREVIEW_|Error|Traceback" 
ls -la art/blender/ship.blend game/assets/models/ship.glb art/refs/preview-ship-*.png 2>/dev/null
```
Expected: `SHIP_TRIS` в диапазоне 450–800 (расчёт: около 500), `SHIP_DIMS` около `(3.4, 4.3, 1.9)`, `SHIP_GLB ... <размер>`, три `PREVIEW_WRITTEN` или одна строка `PREVIEW_SKIPPED` с причиной. Если `SHIP_TRIS` вне диапазона или `SHIP_DIMS` отклоняется больше чем на 0.3 по любой оси, не подгонять числа молча: доложить DONE_WITH_CONCERNS с измерениями.

Если превью записаны, открыть `art/refs/preview-ship-rear.png` через Read: кремовый корпус, оранжевая полоса, синее сопло с циановым кольцом, жёлтые усики, крылышки с оранжевыми концами.

- [ ] **Step 7: Commit**

```bash
git add art/blender/lib/materials.py art/blender/lib/build.py art/blender/lib/export.py art/blender/lib/preview.py art/blender/scripts/ship.py art/blender/ship.blend game/assets/models/ship.glb
git add art/refs/preview-ship-*.png 2>/dev/null || true
git commit -m "feat(art): библиотека сборки bmesh и корабль игрока «Жук» в .blend и .glb"
```

---

### Task 3: Проверка моделей и переэкспорт

**Files:**
- Create: `art/check_models.py`, `art/export.py`

**Interfaces:**
- Consumes: `lib.export.export_glb`.
- Produces: `scripts/art.sh check` (код 0/1), `scripts/art.sh export`.

- [ ] **Step 1: Создать `art/check_models.py`**

```python
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
```

Примечание: `sys.exit(1)` внутри Blender завершает процесс с кодом 1 даже без `--python-exit-code`; флаг остаётся для необработанных исключений.

- [ ] **Step 2: Создать `art/export.py`**

```python
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
```

- [ ] **Step 3: Прогнать проверку и переэкспорт**

```bash
scripts/art.sh check 2>&1 | rg "CHECK|FAIL|Error|Traceback"; echo "exit=${PIPESTATUS[0]}"
scripts/art.sh export 2>&1 | rg "EXPORTED|EXPORT_|Error|Traceback"; echo "exit=${PIPESTATUS[0]}"
scripts/art.sh check 2>&1 | rg "CHECK_RESULT"
git status --short
```
Expected: первая проверка `CHECK_RESULT OK`, exit 0; экспорт `EXPORTED ship ...`, exit 0; повторная проверка `OK`. `git status` может показать изменённый `ship.glb` после переэкспорта (бинарно другой из-за метаданных) — это нормально, коммитим актуальный.

Негативная проверка лимитов: временно поменять в `LIMITS` `"tris": (1, 2)`, прогнать `scripts/art.sh check`, убедиться в `FAIL` и exit 1, вернуть значение. Записать в отчёт.

- [ ] **Step 4: Commit**

```bash
git add art/check_models.py art/export.py game/assets/models/ship.glb
git commit -m "feat(art): проверка .glb по style-guide и переэкспорт .blend"
```

---

### Task 4: Корабль в игре

**Files:**
- Create (generated): `game/assets/models/ship.glb.import`, `docs/playtests/shot-ship.png`, `docs/playtests/shot-ship-6s.png`
- Modify: ничего в коде. Если корабль встал не носом вперёд или не по центру капсулы, остановиться и доложить, не подгонять сцену.

**Interfaces:**
- Consumes: `ModelSlot` (Task 11 этапа 2) ищет `res://assets/models/ship.glb` и скрывает заглушку.

- [ ] **Step 1: Импорт и headless-прогон**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -2
scripts/art.sh import 2>&1 | rg -i "error" || echo "import clean"
"$GODOT" --headless --path game --quit-after 300 2>&1 | rg "ERROR|SCRIPT ERROR|Unhandled|WARNING" | sort | uniq -c
ls game/assets/models/
```
Expected: `import clean`; в прогоне нет `ERROR`; предупреждения `ModelSlot` есть только для `asteroid`, `enemy_drone`, `enemy_shooter`, для `ship.glb` предупреждения нет; в папке появился `ship.glb.import`.

- [ ] **Step 2: Скриншоты**

```bash
scripts/art.sh shot 2.5 res://../docs/playtests/shot-ship.png 2>&1 | rg "screenshot"
scripts/art.sh shot 6 res://../docs/playtests/shot-ship-6s.png 2>&1 | rg "screenshot"
```
Открыть оба PNG через Read. Критерии: капсулы нет; виден кремовый корпус с оранжевой полосой, тёмно-синее сопло с циановым кольцом обращено к камере, жёлтые усики уходят от камеры (нос вперёд, −Z), корабль освещён сверху, центр корабля около (640, 400) px как у капсулы раньше. Если сопло смотрит от камеры, а усики к камере, значит ось перепутана: доложить DONE_WITH_CONCERNS.

- [ ] **Step 3: Commit**

```bash
git add game/assets/models/ship.glb.import docs/playtests/shot-ship.png docs/playtests/shot-ship-6s.png
git commit -m "feat(art): корабль «Жук» импортирован в Godot, скриншоты в игре"
```

---

### Task 5: Документация пайплайна

**Files:**
- Modify: `CLAUDE.md`, `README.md`, `docs/style-guide.md`

- [ ] **Step 1: `CLAUDE.md`** — в раздел «Структура» заменить строку про `art/` на:
```markdown
- `art/blender/lib/` — bpy-библиотека (палитра, материалы, сборка, экспорт). `art/blender/scripts/` — генераторы моделей. `art/blender/*.blend` — источник правды после ручных правок. `art/refs/` — концепты и превью.
```
В раздел «Команды» добавить блок:
```markdown
Арт-пайплайн (Blender 5.2 headless, точка входа `scripts/art.sh`):
```bash
scripts/art.sh test           # unittest палитры (обычный Python)
scripts/art.sh make-palette   # art/blender/palette.png + копия в game/assets/textures
scripts/art.sh ship           # строит корабль: ship.blend, ship.glb, превью
scripts/art.sh export         # переэкспорт всех .blend после ручных правок
scripts/art.sh check          # лимиты полигонажа и габаритов .glb, код 1 при нарушении
scripts/art.sh import         # Godot --import, чтобы ModelSlot увидел новые .glb
scripts/art.sh shot 2.5 res://../docs/playtests/shot.png   # скриншот игры
```
```
В раздел «Конвенции» добавить:
```markdown
- Нос модели по +Y в Blender (экспортёр glTF даёт −Z в Godot). Проверять скриншотом, не арифметикой: `.tscn` пишет строки базиса.
- После любого нового .glb обязателен `scripts/art.sh import`, иначе `ResourceLoader.Exists` не видит файл и остаётся заглушка.
- Модели красятся UV в центры ячеек палитры; материалы `palette` и `palette_emit`, других не заводить.
```

- [ ] **Step 2: `README.md`** — добавить раздел после «Тесты»:
```markdown
## Арт

Модели строятся Python-скриптами в Blender 5.2 и экспортируются в `game/assets/models/*.glb`.
Команды: `scripts/art.sh {test|make-palette|ship|export|check|import|shot}`. Подробности в `CLAUDE.md`.
```

- [ ] **Step 3: `docs/style-guide.md`** — в разделе «Цвет» заменить строку про один материал на:
```markdown
- Два материала на все модели: `palette` (базовый цвет из палитры) и `palette_emit`
  (тот же цвет плюс эмиссия силой 3). Ячейки строк 6–7 палитры красятся вторым.
  Раскладка ячеек: `art/blender/lib/palette.py`.
```
В раздел «Экспорт» добавить:
```markdown
- Экспорт делает `lib/export.py`: `GLB`, `export_apply`, `export_yup`, текстура упакована.
- Лимиты проверяет `art/check_models.py`; новые модели добавлять в его таблицу `LIMITS`.
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md README.md docs/style-guide.md
git commit -m "docs: команды арт-пайплайна и правила моделей"
```

---

### Task 6: Приём владельцем

**Files:**
- Create: `docs/playtests/2026-09-05-ship.md`

- [ ] **Step 1: Финальная проверка**

```bash
scripts/art.sh test 2>&1 | tail -2
scripts/art.sh check 2>&1 | rg CHECK_RESULT
dotnet test game/SpaceRail.sln 2>&1 | tail -1
"$GODOT" --headless --path game --quit-after 300 2>&1 | rg -c "ERROR|SCRIPT ERROR|Unhandled" || echo "smoke clean"
git status --short
```
Expected: `OK`, `CHECK_RESULT OK`, 9 тестов, `smoke clean`, дерево чистое.

- [ ] **Step 2: Запустить игру владельцу**

```bash
"$GODOT" --path game
```
Вопросы: 1) корабль читается как «Жук» с концепта? 2) масштаб относительно астероидов и коридора нормальный? 3) что поправить в модели до перехода к врагам?

- [ ] **Step 3: Записать ответы и решение в `docs/playtests/2026-09-05-ship.md`** (дата, коммит, ответы, CONTINUE/ADJUST, что дальше) и закоммитить: `docs: приём корабля игрока`.

---

## Самопроверка плана

**Покрытие спеки.** Раздел 3 (файлы): Task 1 (`palette.py`, тесты, `make_palette.py`, `art.sh`), Task 2 (`materials`, `build`, `export`, `preview`, `ship.py`), Task 3 (`check_models.py`, `export.py`). Раздел 4 (палитра): Task 1. Раздел 5 (геометрия): Task 2, таблица частей перенесена в `ship.py` один в один. Раздел 6 (проверки): unittest в Task 1, `check_models` в Task 3, Godot и скриншот в Task 4, владелец в Task 6. Документация: Task 5.

**Согласованность имён.** `palette.cell_uv`, `palette.is_emissive`, `palette.resolve` используются в `build.py` и тестах одинаково. `export.export_glb(obj, path)` вызывают `ship.py` и `art/export.py`. Объект `ship` ищется по имени файла в `art/export.py`. Лимиты в `check_models.py` совпадают с Global Constraints.

**Риски, известные заранее.** EEVEE headless может не подняться: превью объявлено опциональным, критерий приёмки это скриншот Godot. `shade_smooth_by_angle` и `create_cone(radius1=...)` подтверждены пробой на Blender 5.2.1. Порядок пикселей `bpy` (снизу вверх) заложен в `cell_uv` и в тест на центр ячейки.
