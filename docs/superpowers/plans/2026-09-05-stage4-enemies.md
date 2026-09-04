# Этап 4: астероид, дрон, стрелок — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Все заглушки в игре заменены моделями из Blender: три астероида, дрон, стрелок. Обвязка скриптов вынесена в `lib/pipeline.py`, враги смотрят на игрока, лимиты проверяются автоматически.

**Architecture:** `pipeline.run(name, build_fn)` делает всё вокруг геометрии; скрипт модели описывает только `build(b)`. Астероиды это икосфера с детерминированным шумом, три seed. Враги строятся по концепту Codex носом по +Y, сцены поворачивают `Model` на 180°. `ModelSlot` умеет выбирать случайный путь из массива.

**Tech Stack:** Blender 5.2.1 (`bpy`, `bmesh`, `mathutils.noise`), Python 3.12 unittest, Godot 4.7.1 mono, C#.

**Спека:** `docs/superpowers/specs/2026-09-05-stage4-enemies-design.md`.

**Порядок:** задачи 1–3 не зависят от концепта врагов и идут первыми. Задачи 4 (дрон) и 5 (стрелок) дописываются в этот файл после выбора концепта владельцем; задачи 6–7 закрывают этап.

## Global Constraints

- Blender: `"$BLENDER" -b --python-exit-code 1 --python <script>` (флаг строго до `--python`). Через `scripts/art.sh <cmd>`.
- Godot console: `GODOT="/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe"`; `scripts/art.sh import`, `scripts/art.sh shot <sec> <res://out.png>`; headless smoke `"$GODOT" --headless --path game --quit-after 600` без `ERROR`/`SCRIPT ERROR`/`Unhandled exception`.
- Нос модели по Blender +Y. 1 единица = 1 м. Один объект и один меш с именем модели. `Builder.finish(name)` подключает материалы `palette`/`palette_emit`.
- `save_blend` отказывается перезаписывать существующий `.blend` без `ART_OVERWRITE=1`.
- Лимиты (оси Blender после обратного импорта): `ship` 1500–3000 тр., x 3.0–3.8, y 4.0–4.6, z 1.6–2.2; `asteroid_a/b/c` 250–600 тр., каждая ось 2.0–3.8; `enemy_drone` 500–800 тр., x 1.3–1.9, y 1.2–1.8, z 0.35–0.7; `enemy_shooter` 800–1200 тр., x 1.8–2.4, y 1.8–2.4, z 0.7–1.2.
- Палитра врагов: `gray`, `gray_dark`, `navy`, `black`, `emit_red`, `emit_magenta`. Астероид: `rock`, `rock_light`, `rock_dark`. Без кремового, оранжевого, циана у врагов.
- Тесты `art/tests/*` не содержат чисел из `LIMITS`, только ссылки на них.
- Godot `.import` для извлечённых текстур `*_palette.png`: `detect_3d/compress_to=0`.
- UTF-8 без BOM. Conventional Commits на русском, без упоминания LLM. `.uid`, `.import`, `.blend`, `.glb`, PNG коммитятся.
- Все пути в скриптах вычисляются от `__file__`; репозиторий `C:\gamedev\prototype-blender`.

---

## Карта файлов

| Файл | Ответственность |
|---|---|
| `art/blender/lib/pipeline.py` | `run(name, build_fn, render_preview=True)` |
| `art/blender/lib/build.py` | `Builder.adopt(verts, cell)` публичный; детерминированный порядок рёбер в `bevel` |
| `art/blender/scripts/ship.py` | переведён на `pipeline.run`, геометрия без изменений |
| `art/blender/scripts/asteroid.py` | три варианта астероида |
| `art/blender/scripts/enemy_drone.py`, `enemy_shooter.py` | враги (задачи 4–5) |
| `art/check_models.py` | `LIMITS` для всех моделей |
| `art/tests/test_check_models.py` | лимиты из `LIMITS`, проверка структуры таблицы |
| `scripts/art.sh` | команды `asteroid`, `drone`, `shooter`, `models` |
| `game/scripts/ModelSlot.cs` | `ModelPaths` со случайным выбором |
| `game/scenes/Asteroid.tscn` | три пути астероидов |
| `game/scenes/EnemyDrone.tscn`, `EnemyShooter.tscn` | `Model` повёрнут на 180° |
| `docs/style-guide.md`, `CLAUDE.md` | правила и команды |

---

### Task 1: `lib/pipeline.py`, перевод `ship.py`, детерминированный `bevel`, тесты без чисел

**Files:**
- Create: `art/blender/lib/pipeline.py`
- Modify: `art/blender/lib/build.py`, `art/blender/scripts/ship.py`, `art/tests/test_check_models.py`, `scripts/art.sh`

**Interfaces:**
- Produces:
  ```python
  # lib/pipeline.py
  ART_BLENDER: str; REPO: str; PALETTE: str; MODELS: str; REFS: str
  def run(name: str, build_fn, render_preview: bool = True):  # -> bpy.types.Object
      # печатает f"{NAME}_TRIS", f"{NAME}_DIMS", f"{NAME}_GLB"
  # lib/build.py
  Builder.adopt(self, verts, cell) -> list[BMFace]   # публичный аналог _finish_part
  ```
  `scripts/art.sh`: новые команды `asteroid | drone | shooter | models` (`models` = ship, asteroid, drone, shooter подряд).

- [ ] **Step 1: Обновить тесты лимитов, чтобы не содержали чисел (падать не должны, это рефакторинг тестов)**

Заменить содержимое `art/tests/test_check_models.py`:

```python
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from check_models import LIMITS, evaluate  # noqa: E402

LIM = LIMITS["ship"]
TRIS_LO, TRIS_HI = LIM["tris"]
OK_TRIS = (TRIS_LO + TRIS_HI) // 2
OK_DIMS = tuple((LIM[a][0] + LIM[a][1]) / 2 for a in "xyz")


class EvaluateTests(unittest.TestCase):
    def test_valid_model_has_no_problems(self):
        self.assertEqual(evaluate("ship", OK_TRIS, OK_DIMS, LIM), [])

    def test_tris_bounds_are_inclusive(self):
        self.assertEqual(evaluate("ship", TRIS_LO, OK_DIMS, LIM), [])
        self.assertEqual(evaluate("ship", TRIS_HI, OK_DIMS, LIM), [])

    def test_tris_just_outside_bounds_fail(self):
        for tris in (TRIS_LO - 1, TRIS_HI + 1):
            with self.subTest(tris=tris):
                problems = evaluate("ship", tris, OK_DIMS, LIM)
                self.assertEqual(len(problems), 1)
                self.assertIn("треугольников", problems[0])

    def test_each_axis_just_outside_range_fails(self):
        eps = 0.01
        for i, axis in enumerate("xyz"):
            lo, hi = LIM[axis]
            for bad in (lo - eps, hi + eps):
                with self.subTest(axis=axis, value=bad):
                    dims = list(OK_DIMS)
                    dims[i] = bad
                    problems = evaluate("ship", OK_TRIS, tuple(dims), LIM)
                    self.assertEqual(len(problems), 1)
                    self.assertIn(f"размер {axis}=", problems[0])

    def test_axis_bounds_are_inclusive(self):
        for i, axis in enumerate("xyz"):
            for bound in LIM[axis]:
                with self.subTest(axis=axis, value=bound):
                    dims = list(OK_DIMS)
                    dims[i] = bound
                    self.assertEqual(evaluate("ship", OK_TRIS, tuple(dims), LIM), [])

    def test_problems_accumulate(self):
        self.assertEqual(len(evaluate("ship", TRIS_HI * 10, (0.0, 0.0, 0.0), LIM)), 4)


class LimitsTableTests(unittest.TestCase):
    def test_every_entry_has_ordered_ranges(self):
        for name, lim in LIMITS.items():
            with self.subTest(model=name):
                self.assertEqual(set(lim), {"tris", "x", "y", "z"})
                for key, (lo, hi) in lim.items():
                    self.assertLess(lo, hi, f"{name}.{key}")
                    self.assertGreater(lo, 0, f"{name}.{key}")

    def test_expected_models_present(self):
        self.assertIn("ship", LIMITS)
```

Run: `scripts/art.sh test 2>&1 | tail -3` → `OK`, число тестов 15 (13 было, минус ничего, плюс 2).

- [ ] **Step 2: Создать `art/blender/lib/pipeline.py`**

```python
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
```

- [ ] **Step 3: `art/blender/lib/build.py`: публичный `adopt` и детерминированный `bevel`**

Добавить метод после `box`:
```python
    def adopt(self, verts, cell):
        """Принять уже созданные вершины (например, из bmesh.ops) как часть модели и покрасить их грани."""
        return self._finish_part(verts, cell)
```

В `bevel` заменить строку `edges = list({e for f in faces if f.is_valid for e in f.edges})` на:
```python
        def edge_key(e):
            a, c = (tuple(round(x, 5) for x in v.co) for v in e.verts)
            return tuple(sorted((a, c)))

        # Порядок рёбер фиксирован по координатам: bmesh.ops.bevel зависит от порядка
        # входа, а итерация по set() меняется от запуска к запуску и давала разные байты .glb.
        edges = sorted({e for f in faces if f.is_valid for e in f.edges}, key=edge_key)
```

- [ ] **Step 4: Перевести `art/blender/scripts/ship.py` на `pipeline.run`**

Заменить шапку (строки до `b = build.Builder()`) на:
```python
"""Корабль игрока «Жук». Запуск: ART_OVERWRITE=1 scripts/art.sh ship."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mathutils import Vector  # noqa: E402

from lib import pipeline  # noqa: E402
from lib.build import center  # noqa: E402
```
Всю геометрию (от `# --- корпус` до `belly = ...; b.bevel(belly, ...)`) обернуть в функцию `def build(b):` с отступом; константы `HULL`, `DRUM`, `DRUM_SCALE`, `WING_ROOT_X` и вспомогательные функции `sweep`, `tilt` могут остаться на уровне модуля. Хвост файла (`ship = b.finish(...)`, три `print`, `export.save_blend`, `export.export_glb`, `print("SHIP_GLB"...)`, `preview.render_views`) заменить на одну строку:
```python
pipeline.run("ship", build)
```
Убрать неиспользуемые импорты (`bpy`, `build`, `export`, `materials`, `preview`, `PALETTE/BLEND/GLB/PREVIEW`).

- [ ] **Step 5: Добавить команды в `scripts/art.sh`**

После строки `ship)` добавить:
```bash
  asteroid)     blender_run "$ROOT/art/blender/scripts/asteroid.py" ;;
  drone)        blender_run "$ROOT/art/blender/scripts/enemy_drone.py" ;;
  shooter)      blender_run "$ROOT/art/blender/scripts/enemy_shooter.py" ;;
  models)       for m in ship asteroid drone shooter; do "$0" "$m"; done ;;
```
Обновить строку `usage`, добавив `asteroid|drone|shooter|models`.

- [ ] **Step 6: Проверка эквивалентности и детерминизма**

```bash
scripts/art.sh test 2>&1 | tail -2
ART_OVERWRITE=1 scripts/art.sh ship 2>&1 | rg "SHIP_|PREVIEW_|Error|Traceback"
sha256sum game/assets/models/ship.glb
ART_OVERWRITE=1 scripts/art.sh ship 2>&1 | rg "SHIP_TRIS"
sha256sum game/assets/models/ship.glb
scripts/art.sh check 2>&1 | rg "CHECK"
```
Expected: 15 тестов OK; `SHIP_TRIS 2558`, `SHIP_DIMS (3.5, 4.37, 1.96)` как до рефакторинга; две суммы `ship.glb` подряд **совпадают** (детерминизм bevel); `CHECK_RESULT OK`. Если суммы различаются, найти источник недетерминизма (другие `set()` в `deform`/`bevel`) и устранить, не коммитить до совпадения.

- [ ] **Step 7: Commit**

```bash
git add art/blender/lib/pipeline.py art/blender/lib/build.py art/blender/scripts/ship.py art/tests/test_check_models.py scripts/art.sh art/blender/ship.blend game/assets/models/ship.glb art/refs/preview-ship-*.png
git commit -m "refactor(art): pipeline.run для скриптов моделей, детерминированный bevel, тесты без чисел"
```

---

### Task 2: Три астероида

**Files:**
- Create: `art/blender/scripts/asteroid.py`
- Modify: `art/check_models.py`
- Create (generated): `art/blender/asteroid_{a,b,c}.blend`, `game/assets/models/asteroid_{a,b,c}.glb`, `art/refs/preview-asteroid_*-*.png`

**Interfaces:**
- Consumes: `pipeline.run`, `Builder.adopt`, `Builder.paint`.
- Produces: `LIMITS["asteroid_a"|"asteroid_b"|"asteroid_c"]`.

- [ ] **Step 1: Создать `art/blender/scripts/asteroid.py`**

```python
"""Три варианта астероида из икосферы: детерминированный шум по вершинам. Запуск: scripts/art.sh asteroid."""
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bmesh  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

from lib import pipeline  # noqa: E402

VARIANTS = {"asteroid_a": 11, "asteroid_b": 23, "asteroid_c": 37}
RADIUS = 1.5          # под коллайдер SphereShape3D r=1.5
BUMP = 0.20           # крупные неровности
GRAIN = 0.05          # мелкая шероховатость
DARK_SHARE = 0.15     # доля тёмных пятен


def make_build(seed: int):
    def build(b):
        rng = random.Random(seed)
        shell = bmesh.ops.create_icosphere(b.bm, subdivisions=2, radius=1.0)
        verts = shell["verts"]
        offset = Vector((rng.uniform(-40.0, 40.0) for _ in range(3)))
        for v in verts:
            big = noise.noise(v.co * 1.6 + offset)
            fine = noise.noise(v.co * 4.5 + offset * 0.5)
            v.co = v.co * (1.0 + BUMP * big + GRAIN * fine)
        axes = [1.0, 0.9, 0.8]
        rng.shuffle(axes)
        bmesh.ops.transform(b.bm, matrix=Matrix.Diagonal((*axes, 1.0)) * RADIUS, verts=verts)
        faces = b.adopt(verts, "rock")
        b.paint([f for f in faces if f.normal.z > 0.55], "rock_light")
        b.paint([f for f in faces if rng.random() < DARK_SHARE], "rock_dark")
    return build


for name, seed in VARIANTS.items():
    pipeline.run(name, make_build(seed))
```

Примечание: `Matrix.Diagonal(...) * RADIUS` умножает все элементы, включая последний `1.0 * RADIUS`; для `bmesh.ops.transform` важна только верхняя 3×3 часть, но чтобы не полагаться на это, писать `Matrix.Diagonal((axes[0] * RADIUS, axes[1] * RADIUS, axes[2] * RADIUS, 1.0))`.

- [ ] **Step 2: Добавить лимиты в `art/check_models.py`**

```python
ASTEROID = {"tris": (250, 600), "x": (2.0, 3.8), "y": (2.0, 3.8), "z": (2.0, 3.8)}
LIMITS = {
    "ship": {"tris": (1500, 3000), "x": (3.0, 3.8), "y": (4.0, 4.6), "z": (1.6, 2.2)},
    "asteroid_a": ASTEROID,
    "asteroid_b": ASTEROID,
    "asteroid_c": ASTEROID,
}
```

- [ ] **Step 3: Собрать и проверить**

```bash
scripts/art.sh asteroid 2>&1 | rg "ASTEROID_|PREVIEW_WRITTEN|Error|Traceback"
scripts/art.sh check 2>&1 | rg "CHECK"
scripts/art.sh test 2>&1 | tail -1
```
Expected: три блока `ASTEROID_X_TRIS 320`, `ASTEROID_X_DIMS` с каждой осью в 2.0–3.8 и заметно разными пропорциями между вариантами; `CHECK_RESULT OK`; тесты OK. Открыть `art/refs/preview-asteroid_a-rear.png` и `-side.png` через Read: бугристый камень, светлее сверху, тёмные пятна, без плоских граней-«зеркал».

Если какая-то ось выходит за лимит, уменьшить `BUMP` до 0.15 и пересобрать (`ART_OVERWRITE=1`).

- [ ] **Step 4: Commit**

```bash
git add art/blender/scripts/asteroid.py art/check_models.py art/blender/asteroid_*.blend game/assets/models/asteroid_*.glb art/refs/preview-asteroid_*
git commit -m "feat(art): три варианта астероида из икосферы с детерминированным шумом"
```

---

### Task 3: Godot: случайный вариант модели и ориентация врагов

**Files:**
- Modify: `game/scripts/ModelSlot.cs`, `game/scenes/Asteroid.tscn`, `game/scenes/EnemyDrone.tscn`, `game/scenes/EnemyShooter.tscn`
- Create (generated): `game/assets/models/asteroid_*.glb.import`, `asteroid_*_palette.png` + `.import`, `docs/playtests/shot-asteroids.png`

**Interfaces:**
- Produces: `ModelSlot.ModelPaths: string[]`; выбор `Random.Shared.Next`.

- [ ] **Step 1: `game/scripts/ModelSlot.cs`**

Заменить тело класса:
```csharp
public partial class ModelSlot : Node3D
{
    private static readonly HashSet<string> Reported = new();

    /// <summary>Один путь к модели. Используется, если ModelPaths пуст.</summary>
    [Export] public string ModelPath { get; set; } = "";

    /// <summary>Несколько вариантов модели: при появлении в сцене берётся случайный.</summary>
    [Export] public string[] ModelPaths { get; set; } = System.Array.Empty<string>();

    public override void _Ready()
    {
        var path = ModelPaths.Length > 0 ? ModelPaths[Random.Shared.Next(ModelPaths.Length)] : ModelPath;
        if (string.IsNullOrEmpty(path)) return;

        var placeholder = GetNodeOrNull<Node3D>("Placeholder");
        if (!ResourceLoader.Exists(path))
        {
            if (Reported.Add(path))
                GD.PushWarning($"ModelSlot: {path} не найден, остаётся заглушка");
            return;
        }

        var scene = ResourceLoader.Load<PackedScene>(path);
        if (scene is null)
        {
            GD.PushWarning($"ModelSlot: {path} не удалось загрузить как PackedScene, остаётся заглушка");
            return;
        }

        AddChild(scene.Instantiate<Node3D>());
        if (placeholder is not null) placeholder.Visible = false;
    }
}
```

- [ ] **Step 2: `game/scenes/Asteroid.tscn`**

В узле `Model` заменить строку `ModelPath = "res://assets/models/asteroid.glb"` на:
```
ModelPaths = PackedStringArray("res://assets/models/asteroid_a.glb", "res://assets/models/asteroid_b.glb", "res://assets/models/asteroid_c.glb")
```

- [ ] **Step 3: Поворот `Model` во вражеских сценах**

В `game/scenes/EnemyDrone.tscn` и `game/scenes/EnemyShooter.tscn` в узле `Model` после строки `[node name="Model" type="Node3D" parent="."]` добавить:
```
transform = Transform3D(-1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0)
```
(поворот на 180° вокруг Y: строки базиса `[-1,0,0; 0,1,0; 0,0,-1]`; модель носом по −Z в glTF станет смотреть на игрока по +Z).

- [ ] **Step 4: Сборка, импорт, прогон, скриншот**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -2
scripts/art.sh import 2>&1 | rg -i "error" || echo "import clean"
"$GODOT" --headless --path game --quit-after 600 2>&1 | rg "ERROR|WARNING" | sort | uniq -c
rg -n "compress_to" game/assets/models/asteroid_*_palette.png.import
scripts/art.sh shot 8 res://../docs/playtests/shot-asteroids.png 2>&1 | rg screenshot
```
Expected: сборка чистая; `import clean`; предупреждения `ModelSlot` только для `enemy_drone.glb` и `enemy_shooter.glb`; `compress_to=0` в трёх `.import` (если Godot записал `1`, поправить на `0` вручную и повторить `import`); на скриншоте два и более астероида разной формы, коричневые с светлым верхом, корабль на месте. Если астероиды отсутствуют на кадре, повторить с `shot 12`.

- [ ] **Step 5: Commit**

```bash
git add game/scripts/ModelSlot.cs game/scenes/Asteroid.tscn game/scenes/EnemyDrone.tscn game/scenes/EnemyShooter.tscn game/assets/models/asteroid_* docs/playtests/shot-asteroids.png
git commit -m "feat: ModelSlot выбирает случайный вариант, астероиды в игре, Model врагов повёрнут к игроку"
```

---

### Task 4: Дрон

Концепт: `art/refs/concept-enemies-main.png` (слева) и `concept-enemies-ortho.png` (верхний ряд). Плоский клин-дельта, тёмно-синий гребень по оси, два скошенных плавника на концах, красный сенсор-глаз на носу в сером кольце, красный двигатель сзади сверху.

**Files:**
- Create: `art/blender/scripts/enemy_drone.py`
- Modify: `art/check_models.py` (`LIMITS["enemy_drone"]`)
- Create (generated): `art/blender/enemy_drone.blend`, `game/assets/models/enemy_drone.glb` (+ `.import`, `enemy_drone_palette.png` + `.import` после Task 5 импорта), `art/refs/preview-enemy_drone-*.png`

**Interfaces:**
- Consumes: `pipeline.run`, `Builder.box/cylinder/deform/bevel/paint`, `center`.
- Produces: `LIMITS["enemy_drone"] = {"tris": (500, 800), "x": (1.3, 1.9), "y": (1.2, 1.8), "z": (0.35, 0.7)}`.

- [ ] **Step 1: Создать `art/blender/scripts/enemy_drone.py`**

```python
"""Враг-дрон: плоский клин с красным глазом. Нос по +Y. Запуск: scripts/art.sh drone."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mathutils import Vector  # noqa: E402

from lib import pipeline  # noqa: E402
from lib.build import center  # noqa: E402

NOSE_Y, TAIL_Y = 0.78, -0.72


def taper(v):
    """К носу клин сужается по X почти в точку и слегка сплющивается по Z."""
    t = min(max((v.y - TAIL_Y) / (NOSE_Y - TAIL_Y), 0.0), 1.0)
    return Vector((v.x * (1.0 - 0.88 * t), v.y, v.z * (1.0 - 0.35 * t)))


def fin_lean(v):
    """Плавники отклоняются наружу и вверх к задней кромке."""
    t = min(max((TAIL_Y - v.y) / 0.5 + 0.5, 0.0), 1.0)
    side = 1.0 if v.x > 0 else -1.0
    return Vector((v.x + side * 0.12 * t, v.y, v.z + 0.10 * t))


def build(b):
    body = b.box((1.50, NOSE_Y - TAIL_Y, 0.34), (0.0, (NOSE_Y + TAIL_Y) / 2, 0.0), "gray")
    b.deform(body, taper)
    body = b.bevel(body, offset=0.03, segments=2, cell="gray")
    b.paint([f for f in body if f.normal.z < -0.5], "gray_dark")

    spine = b.box((0.34, 1.10, 0.14), (0.0, -0.02, 0.20), "navy")
    b.deform(spine, taper)
    b.bevel(spine, offset=0.02, segments=2, cell="navy")

    # Глаз: серое кольцо и красное эмиссивное ядро на самом носу.
    ring = b.cylinder(12, 0.17, 0.14, (0.0, NOSE_Y + 0.02, 0.0), "gray_dark", axis="Y")
    core = b.cylinder(12, 0.10, 0.16, (0.0, NOSE_Y + 0.03, 0.0), "emit_red", axis="Y")
    b.paint([f for f in ring if f.normal.y > 0.9], "navy")

    for sx in (-1.0, 1.0):
        fin = b.box((0.08, 0.46, 0.26), (sx * 0.70, -0.50, 0.14), "navy")
        b.deform(fin, fin_lean)
        b.bevel(fin, offset=0.015, segments=1, cell="navy")

    engine = b.box((0.36, 0.26, 0.18), (0.0, TAIL_Y - 0.02, 0.10), "navy")
    engine = b.bevel(engine, offset=0.02, segments=1, cell="navy")
    b.paint([f for f in engine if f.normal.y < -0.9], "emit_red")


pipeline.run("enemy_drone", build)
```

- [ ] **Step 2: Лимит** — в `art/check_models.py` добавить в `LIMITS`:
```python
    "enemy_drone": {"tris": (500, 800), "x": (1.3, 1.9), "y": (1.2, 1.8), "z": (0.35, 0.7)},
```

- [ ] **Step 3: Собрать и проверить**

```bash
scripts/art.sh drone 2>&1 | rg "ENEMY_DRONE_|PREVIEW_WRITTEN|Error|Traceback"
scripts/art.sh check 2>&1 | rg "CHECK"
```
Expected: `ENEMY_DRONE_TRIS` в 500–800, `ENEMY_DRONE_DIMS` около `(1.6, 1.6, 0.5)` в лимитах, `CHECK_RESULT OK`. Открыть `art/refs/preview-enemy_drone-top.png` и `-side.png`: клин, тёмный гребень, красный глаз на носу, плавники, красный блок сзади. Если полигонаж ниже 500, поднять `segments` фаски корпуса до 3; если выше 800, снизить до 1 у плавников и двигателя.

- [ ] **Step 4: Commit**

```bash
git add art/blender/scripts/enemy_drone.py art/check_models.py art/blender/enemy_drone.blend game/assets/models/enemy_drone.glb art/refs/preview-enemy_drone-*
git commit -m "feat(art): враг-дрон по концепту, клин с красным сенсором"
```

---

### Task 5: Стрелок и оба врага в игре

Концепт: `art/refs/concept-enemies-main.png` (справа) и `concept-enemies-ortho.png` (нижний ряд). Широкий бронированный корпус, тёмно-синий продольный паз по центру верха, два плечевых блока, два боковых цилиндрических излучателя с маджентовым свечением вперёд, ряд из четырёх красных сенсоров-щелей спереди внизу, два красных двигателя сверху сзади.

**Files:**
- Create: `art/blender/scripts/enemy_shooter.py`
- Modify: `art/check_models.py` (`LIMITS["enemy_shooter"]`)
- Create (generated): `art/blender/enemy_shooter.blend`, `game/assets/models/enemy_shooter.glb`, все `.import` и `*_palette.png` для обоих врагов, `art/refs/preview-enemy_shooter-*.png`, `docs/playtests/shot-enemies.png`

**Interfaces:**
- Produces: `LIMITS["enemy_shooter"] = {"tris": (800, 1200), "x": (1.8, 2.4), "y": (1.8, 2.4), "z": (0.7, 1.2)}`.

- [ ] **Step 1: Создать `art/blender/scripts/enemy_shooter.py`**

```python
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
    """Плечевые блоки уходят назад к внешнему краю."""
    t = min(max((abs(v.x) - 0.55) / 0.6, 0.0), 1.0)
    return Vector((v.x, v.y - 0.25 * t, v.z - 0.05 * t))


def build(b):
    hull = b.box((1.40, FRONT_Y - REAR_Y, 0.70), (0.0, 0.0, 0.0), "gray")
    b.deform(hull, nose_taper)
    hull = b.bevel(hull, offset=0.06, segments=3, cell="gray")
    b.paint([f for f in hull if f.normal.z < -0.6], "gray_dark")

    slot = b.box((0.44, 1.20, 0.16), (0.0, 0.15, 0.36), "navy")
    b.deform(slot, nose_taper)
    b.bevel(slot, offset=0.02, segments=2, cell="navy")

    for sx in (-1.0, 1.0):
        shoulder = b.box((0.60, 1.00, 0.44), (sx * 0.85, 0.10, 0.12), "gray")
        b.deform(shoulder, shoulder_sweep)
        b.bevel(shoulder, offset=0.04, segments=2, cell="gray")

        pod = b.cylinder(12, 0.21, 0.90, (sx * 0.95, 0.50, -0.14), "gray_dark", axis="Y")
        b.paint([f for f in pod if f.normal.y > 0.9], "navy")
        b.cylinder(12, 0.12, 0.16, (sx * 0.95, 0.98, -0.14), "emit_magenta", axis="Y")

        engine = b.cylinder(12, 0.16, 0.36, (sx * 0.45, REAR_Y - 0.05, 0.34), "navy", axis="Y")
        b.paint([f for f in engine if f.normal.y < -0.9], "emit_red")

    for gx in (-0.42, -0.14, 0.14, 0.42):
        b.box((0.18, 0.06, 0.08), (gx, FRONT_Y * (1.0 - 0.0) + 0.0, -0.16), "emit_red")


pipeline.run("enemy_shooter", build)
```

Примечание к сенсорам: коробки стоят на плоскости носа `y = FRONT_Y`; после `nose_taper` корпус в этой зоне уже сужен по X до 0.82 и по Z до 0.78, поэтому `gx = ±0.42` остаётся внутри ширины 1.15, а `z = −0.16` внутри половины высоты 0.27. Если сенсоры уходят внутрь корпуса и не видны на превью, сместить их на `y = FRONT_Y + 0.03`.

- [ ] **Step 2: Лимит** — добавить в `LIMITS`:
```python
    "enemy_shooter": {"tris": (800, 1200), "x": (1.8, 2.4), "y": (1.8, 2.4), "z": (0.7, 1.2)},
```

- [ ] **Step 3: Собрать и проверить**

```bash
scripts/art.sh shooter 2>&1 | rg "ENEMY_SHOOTER_|PREVIEW_WRITTEN|Error|Traceback"
scripts/art.sh check 2>&1 | rg "CHECK"
scripts/art.sh test 2>&1 | tail -1
```
Expected: `ENEMY_SHOOTER_TRIS` в 800–1200, `ENEMY_SHOOTER_DIMS` около `(2.3, 2.1, 0.9)`, `CHECK_RESULT OK`, тесты OK. Превью `-top` и `-side`: широкий корпус, паз, плечи, два ствола вперёд, красные двигатели сзади.

- [ ] **Step 4: Оба врага в игре**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -1
scripts/art.sh import 2>&1 | rg -i "error" || echo "import clean"
"$GODOT" --headless --path game --quit-after 900 2>&1 | rg "ERROR|WARNING" | sort | uniq -c
rg -n "compress_to" game/assets/models/enemy_*_palette.png.import
scripts/art.sh shot 10 res://../docs/playtests/shot-enemies.png 2>&1 | rg screenshot
```
Expected: `import clean`; ни одного предупреждения `ModelSlot` (все пять моделей найдены); `compress_to=0` (иначе поправить и повторить импорт); на скриншоте хотя бы один враг **носом к камере**: у дрона виден красный глаз, у стрелка маджентовые излучатели и красная полоса сенсоров. Если на кадре врагов нет, повторить `shot 14` и `shot 18`, сохранить удачный как `shot-enemies.png`. Если враг виден кормой (красные двигатели к камере, глаз не виден), поворот `Model` в сцене не применился: остановиться и доложить.

- [ ] **Step 5: Commit**

```bash
git add art/blender/scripts/enemy_shooter.py art/check_models.py art/blender/enemy_shooter.blend game/assets/models/enemy_* art/refs/preview-enemy_shooter-* docs/playtests/shot-enemies.png
git commit -m "feat(art): враг-стрелок по концепту, оба врага в игре носом к игроку"
```

---

### Task 6: Документация

**Files:**
- Modify: `docs/style-guide.md`, `CLAUDE.md`

- [ ] **Step 1: `docs/style-guide.md`** — в раздел «Геометрия» добавить:
```markdown
- Враги строятся носом по +Y, как всё; разворот к игроку делает сцена
  (`Model` повёрнут на 180° в `EnemyDrone.tscn`/`EnemyShooter.tscn`).
- Астероиды: икосфера subdiv 2 + шум, три варианта `asteroid_a/b/c`, выбор в
  игре случайный через `ModelSlot.ModelPaths`.
```
В раздел «Цвет» добавить:
```markdown
- Враги: `gray`, `gray_dark`, `navy`, `black`, эмиссия `emit_red` (сенсоры,
  двигатели) и `emit_magenta` (оружие). Кремовый, оранжевый и циан только у игрока.
```

- [ ] **Step 2: `CLAUDE.md`** — в блок команд арт-пайплайна добавить строки:
```bash
scripts/art.sh asteroid       # три астероида
scripts/art.sh drone          # дрон
scripts/art.sh shooter        # стрелок
scripts/art.sh models         # все модели подряд (нужен ART_OVERWRITE=1 для пересборки)
```
В «Конвенции» добавить: `- Скрипт модели содержит только build(b); обвязка в lib/pipeline.py.`

- [ ] **Step 3: Commit**

```bash
git add docs/style-guide.md CLAUDE.md
git commit -m "docs: команды моделей этапа 4, правила врагов и астероидов"
```

---

### Task 7: Приём владельцем

- [ ] Финальная проверка: `scripts/art.sh test`, `scripts/art.sh check`, `dotnet test game/SpaceRail.sln`, headless без `ERROR` и без предупреждений `ModelSlot`.
- [ ] Запуск игры владельцу: `"$GODOT" --path game`. Вопросы: 1) астероиды читаются как камни, а не шары? 2) враги читаются как чужая фракция и видно, что они смотрят на тебя? 3) что поправить до этапа эффектов?
- [ ] Записать ответы и решение в `docs/playtests/2026-09-0X-enemies.md`, закоммитить `docs: приём моделей этапа 4`.

---

## Самопроверка плана (задачи 1–3, 6–7)

**Покрытие спеки.** §2 обвязка: Task 1. §4 астероид: Task 2. §5 игра: Task 3. §6 проверки: Task 1 (тесты), Task 2–3 (check, headless, скриншот), Task 7 (владелец). §3 файлы `enemy_*`: Tasks 4–5 после концепта.

**Согласованность имён.** `pipeline.run(name, build_fn)` печатает `NAME_TRIS`; `check_models` ищет `game/assets/models/<name>.glb` по ключам `LIMITS`; `ModelPaths` в `.tscn` совпадают с `VARIANTS` в `asteroid.py`.
